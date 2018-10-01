LOG_DIR=/var/ftp/tempeh/
LOG_FILE=${LOG_DIR}/$(date +%F_%R)

echo Starting in ${LOG_DIR}
touch ${LOG_FILE}
chmod 744 ${LOG_FILE}
python regulator.py | tee -a ${LOG_FILE}
