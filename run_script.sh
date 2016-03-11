#run to start redis
redis-server

# run this to insert data into redis
python stream_connect.py | python entities.py | python store_redis.py

# run this to start event detection poller

python event_poller.py


#run this to start api server

python concert_api.py

#go here to see current distribution
