#!/usr/bin/env python3
import os
import tarfile
import datetime
import pickle
import time

ORIGEN = "/home/usuario/datos"
DESTINO = "/etc/backup"
META_FILE = os.path.join(DESTINO, "metadata.pkl")
FULL_DAY = 1       # día del mes para backup completo
INC_DAYS = 3       # cada cuantos días se hace incremental
SLEEP_INTERVAL = 24 * 3600  # 1 día

def cargar_metadata():
    if os.path.exists(META_FILE):
        with open(META_FILE, "rb") as f:
            return pickle.load(f)
    return {}

def guardar_metadata(meta):
    with open(META_FILE, "wb") as f:
        pickle.dump(meta, f)

def crear_backup(tipo="full"):
    fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(DESTINO, f"{tipo}_{fecha}.tar.gz")
    meta = cargar_metadata()

    with tarfile.open(backup_file, "w:gz") as tar:
        for root, dirs, files in os.walk(ORIGEN):
            for file in files:
                filepath = os.path.join(root, file)
                mtime = os.path.getmtime(filepath)

                if tipo == "full":
                    tar.add(filepath, arcname=os.path.relpath(filepath, ORIGEN))
                    meta[filepath] = mtime
                elif tipo in ["inc", "daily"]:
                    if filepath not in meta or meta[filepath] < mtime:
                        tar.add(filepath, arcname=os.path.relpath(filepath, ORIGEN))
                        meta[filepath] = mtime

    guardar_metadata(meta)
    print(f"{tipo.capitalize()} backup creado: {backup_file}")

def main():
    os.makedirs(DESTINO, exist_ok=True)
    while True:
        dia = datetime.datetime.now().day

        if dia == FULL_DAY:
            crear_backup("full")
        elif dia != FULL_DAY and dia % INC_DAYS == 0:
            crear_backup("inc")
        else:
            crear_backup("daily")

        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main()
