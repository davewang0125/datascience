""" create new dataset from file system """

import uuid
import os
import logging
import contextlib
import wave
from datetime import datetime
from argparse import ArgumentParser
import pathlib

import psycopg2


LOG = logging.getLogger()
AUDIO_FOLDER = "/tmp"
S3_BUCKET_URL = "s3://webex-ai-measurements-pipeline-audio-shards/mandarin_dataset"

lang_name_dict = {
    "zh": "cmn-CN-Standard-B",
    "en": "en-US-Standard-A",
    "es": "es-ES-Standard-B",
    "de": "de-DE-Standard-B",
    "fr": "fr-FR-Standard-B",
    "ko": "ko-KR-standard-B",
}


def get_audio_length(path):
    """get audio info"""
    with contextlib.closing(wave.open(path, "rb")) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate == 16000
        # pcm_data = wf.readframes(wf.getnframes())
        length_ms = int(wf.getnframes() / sample_rate * 1000)
        return length_ms, sample_rate, num_channels


def get_audio_from_folder(args):
    """generate audio via folder"""
    if not args.audio_meeting_id:
        meeting_id = str(uuid.uuid4())
    else:
        meeting_id = args.audio_meeting_id

    dirname = f"{AUDIO_FOLDER}/{args.lang}/{meeting_id}/"
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    # trainingfile = open(outdir + "/summary.txt", "w")
    summary_file = f"{AUDIO_FOLDER}/{args.lang}/summary.json"
    jsonfile = open(summary_file, "w", encoding="utf-8")
    jsonfile.write("[\n")

    # folders = open(args.source_file, "r", encoding="utf-8"))
    audioFiles = pathlib.Path(args.source_file).glob("**/*.wav")
    # textFiles = glob.glob("*.txt")

    count = 0
    evalData = []
    start_offset = 0

    for audioFile in audioFiles:
        count = count + 1

        scriptFile = str(audioFile).replace(".wav", ".txt")
        scriptContent = open(scriptFile, "r", encoding="utf-8")
        script = scriptContent.readlines()[0].strip()

        baseAuioFile = os.path.basename(audioFile)
        # process_each_line(line)
        outfile = f"{AUDIO_FOLDER}/{args.lang}/{baseAuioFile}"

        record = {}
        record["id"] = str(uuid.uuid4())
        # upload to s3
        if outfile.endswith(".wav"):
            shardName = f"{baseAuioFile}"
            wavefile = f"{dirname}{shardName}"
            cmd = f"cp {audioFile} {wavefile}  > /dev/null 2>&1"
            # print("running: ", cmd)
            os.system(cmd)
            audioLen, _, _ = get_audio_length(wavefile)
            end_offset = start_offset + audioLen
            record["s3uri"] = f"{S3_BUCKET_URL}/{args.lang}/{meeting_id}/{shardName}"
            record["metadata"] = {
                "meeting_id": meeting_id,
                "length_ms": audioLen,
                "start_offset_ms": start_offset,
                "end_offset_ms": end_offset,
                "site_name": "mandarin",
                "created_at": datetime.utcnow(),
                "webex_meeting_number": 22346,
                "csi": "",
            }  # type: ignore[assignment]
            record["ref"] = f"{script}"

            evalData.append(record)
            start_offset = end_offset
            jsonfile.write(f"[ wave: {wavefile}, script: {script} ]")
    jsonfile.write("]\n")
    jsonfile.close()

    return evalData, meeting_id


def extract_eval_audio_set(args):
    """create evaluation audio_set"""
    eval_data, meeting_id = get_audio_from_folder(args)
    print("-- Number of shards from sharder: ", len(eval_data))
    if len(eval_data) == 0:
        return None
    return eval_data, meeting_id


def save_to_db(args, eval_data):
    """save the data to database"""
    user = os.environ.get("PGUSER", "postgres")
    password = os.environ.get("PGPASSWORD", "Holiday39")
    host = os.environ.get("PGHOST", "localhost")
    port = os.environ.get("PGPORT", 5432)
    database = os.environ.get("PGDATABASE", "postgres")
    conn = psycopg2.connect(
        database=database, user=user, password=password, host=host, port=port
    )

    sql_file = open("/tmp/output.sql", "w")
    # Setting auto commit false
    conn.autocommit = False
    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    # create new audio set
    audio_set_id = str(uuid.uuid4())
    sql = (
        "INSERT INTO audio_set (id, created_at, filter_language, \
            filter_site_name, filter_source, description) "
        "values ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')".format(
            audio_set_id,
            datetime.utcnow(),
            args.audio_language,
            args.audio_site_name,
            args.audio_source,
            args.description,
        )
    )
    sql_file.write("-- insert audio_set\n ")
    sql_file.write(f"{sql};\n")
    cursor.execute(sql)
    sql_file.write("-- insert audio_shards\n")
    for data in eval_data:
        # temp, delete old row before insert
        sql = "delete from  audio_shards where id = '{0}' ".format(data["id"])
        sql_file.write(f"{sql};\n")
        cursor.execute(sql)

        metadata = data["metadata"]
        language_inferred = args.lang
        if "language_inferred" in metadata:
            language_inferred = metadata["language_inferred"]

        global_participant_id = metadata.get("global_participant_id", "")
        sql = (
            "INSERT INTO audio_shards (id, meeting_id, length_ms, language_inferred, "
            "start_offset_ms, end_offset_ms, "
            "site_name, webex_meeting_number, global_participant_id, trainable_created_at, s3_uri) "
            "values ('{0}', '{1}', {2}, '{3}', {4}, {5},"
            "'{6}', {7}, '{8}', '{9}', "
            "'{10}')".format(
                data["id"],
                metadata["meeting_id"],
                metadata["length_ms"],
                language_inferred,
                metadata["start_offset_ms"],
                metadata["end_offset_ms"],
                metadata["site_name"],
                metadata["webex_meeting_number"],
                global_participant_id,
                metadata["created_at"],
                data["s3uri"],
            )
        )
        sql_file.write(f"{sql};\n")
        cursor.execute(sql)

        # insert row in audio_shard_set
        sql = "INSERT INTO audio_shard_set (audio_set_id, audio_shard_id)\
            values ('{0}', '{1}') ".format(
            audio_set_id, data["id"]
        )
        sql_file.write(f"{sql};\n")
        cursor.execute(sql)

        # insert ground_truth
        ground_truth_id = str(uuid.uuid4())
        sql = "INSERT  INTO ground_truth (id, audio_shard_id, created_at, \
            transcript, speakers, source, language_code) \
            values ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}') ON \
                CONFLICT (id) DO NOTHING".format(
            ground_truth_id,
            data["id"],
            datetime.utcnow(),
            data["ref"].replace("'", "''"),
            "Native",
            "purchased",
            args.lang,
        )
        sql_file.write(f"{sql};\n")
        cursor.execute(sql)

    conn.commit()
    sql_file.close()


def upload_to_s3(dir_name: str, s3bucketdir: str) -> None:
    """upload all the files to s3 recursively"""
    cmd = f"aws s3 cp {dir_name} {s3bucketdir}/ --recursive > /dev/null 2>&1"
    print("-- running: ", cmd)
    os.system(cmd)


if __name__ == "__main__":
    parser = ArgumentParser(description="Audio Shard Creater")
    parser.add_argument("-audio_language", type=str, required=False, default="zh")
    parser.add_argument("-audio_meeting_id", type=str, required=False)
    parser.add_argument(
        "-audio_source", type=str, required=False, default="aidatatang_200h"
    )
    parser.add_argument("-audio_site_name", type=str, default="aidatatang_200h")
    parser.add_argument("-source_file", type=str, default="/tmp/test/")
    parser.add_argument("-outdir", type=str, default="/tmp")
    parser.add_argument("-json", type=str, default="summary.json")
    parser.add_argument("-lang", type=str, default="zh")
    parser.add_argument("-description", type=str, default="manual inserted")

    args = parser.parse_args()

    eval_data, meeting_id = extract_eval_audio_set(args)
    save_to_db(args, eval_data)
    upload_to_s3(
        f"{args.outdir}/{args.lang}/{meeting_id}",
        f"{S3_BUCKET_URL}/{args.lang}/{meeting_id}",
    )
