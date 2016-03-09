# run this to insert data into redis
python stream_connect.py | python analyzer.py | python store_redis.py