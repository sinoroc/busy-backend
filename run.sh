#!/usr/bin/env sh


SERVICE_CONFIGURATION_FILE=/opt/service/config.ini
SERVICE_SETUP_FILE=/opt/service/setup.py
SERVICE_PORT=6543
SERVICE_PID_PATH=/tmp/service.pid
SERVICE_LOG_PID=
SERVICE_LOG_PATH=/tmp/service.log


install_service()
{
    echo "Installing service..."
    pip3 install -q -e .
    echo "Service installation done."
}

start_service()
{
    echo "Starting service..."
    nohup pserve --log-file=${SERVICE_LOG_PATH} --pid-file=${SERVICE_PID_PATH} --reload --monitor-restart ${SERVICE_CONFIGURATION_FILE} &
    echo "Service started."
}

stop_service()
{
    echo "Stopping service..."
    kill -15 $(cat ${SERVICE_PID_PATH})
    echo "Service stopped."
}

wait_service()
{
    local HOST=$1
    local PORT=$2
    echo "Waiting for service [${HOST} ${PORT}]..."
    while ! timeout 1 bash -c "echo > /dev/tcp/${HOST}/${PORT}" 2> /dev/null
    do
        sleep 1
    done
    echo "Service [${HOST} ${PORT}] is ready"
}

wait_service_end()
{
    local HOST=$1
    local PORT=$2
    echo "Waiting for end of service [${HOST} ${PORT}]..."
    while timeout 1 bash -c "echo > /dev/tcp/${HOST}/${PORT}" 2> /dev/null
    do
        sleep 1
    done
    echo "Service [${HOST} ${PORT}] has ended."
}

start_service_log()
{
    echo "Starting log monitor..."
    tail -f ${SERVICE_LOG_PATH} &
    SERVICE_LOG_PID=$!
    wait ${SERVICE_LOG_PID}
}

stop_service_log()
{
    echo "Stopping log monitor..."
    kill -15 ${SERVICE_LOG_PID}
    echo "Log monitor stopped."
}

terminate_service()
{
    stop_service
    wait_service_end localhost ${SERVICE_PORT}
    stop_service_log
    exit
}


trap terminate_service TERM


if [ -e "${SERVICE_SETUP_FILE}" ]
then
    install_service
fi

start_service
wait_service localhost ${SERVICE_PORT}
start_service_log  # Runs until the container closes


# EOF
