LOG_DIR=/var/ftp/tempeh/
LOG_FILE=${LOG_DIR}/$(date +%F_%R)
LOCAL_DIR=$( dirname "${BASH_SOURCE[0]}" )

echo Starting in ${LOG_DIR}
touch ${LOG_FILE}
chmod 744 ${LOG_FILE}
python $LOCAL_DIR/regulator.py | tee -a ${LOG_FILE}
