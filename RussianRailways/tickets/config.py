QUERY_FOR_TRAINS = """
    with suitable_routes as (
        select route_uuid_id
        from route_part
        where start_id = (select id from railway_station where name = (%s))
            and departure >= (%s)
        intersect
        select route_uuid_id
        from route_part
        where stop_uuid_id = (select id from railway_station where name = (%s))
    ),
    route_parts as (
        select *
        from route_part
        where route_uuid_id in (select route_uuid_id from suitable_routes)
    ),
    start_parts as (
        select p.route_uuid_id as route_id,
            rs.name as start_station_name,
            p.departure as start_datetime
        from (
            select *
            from (
                select row_number() over (partition by route_uuid_id order by "order") as row_num, *
                from route_parts
            ) x
            where row_num = 1
        ) as p
        join railway_station rs on p.start_id = rs.id
    ),
    end_parts as (
        select p.route_uuid_id as route_id,
            rs.name as end_station_name,
            p.arrival as end_datetime
        from (
            select *
            from (
                select row_number() over (partition by route_uuid_id order by "order" desc) as row_num, *
                from route_parts
            ) x
            where row_num = 1
        ) as p
        join railway_station rs on p.stop_uuid_id = rs.id
    ),
    departure_parts as (
        select p.route_uuid_id as route_id,
            rs.name as departure_station_name,
            p.arrival as departure_datetime
        from route_part p
        join railway_station rs on p.start_id = rs.id
        where route_uuid_id in (select route_uuid_id from suitable_routes)
            and start_id = (select id from railway_station where name = (%s))
    ),
    arrival_parts as (
        select p.route_uuid_id as route_id,
            rs.name as arrival_station_name,
            p.arrival as arrival_datetime
        from route_part p
        join railway_station rs on p.stop_uuid_id = rs.id
        where route_uuid_id in (select route_uuid_id from suitable_routes)
            and stop_uuid_id = (select id from railway_station where name = (%s))
    )

    select 
        sp.route_id,
        sp.start_station_name,
        sp.start_datetime,
        dp.departure_station_name,
        dp.departure_datetime,
        ap.arrival_station_name,
        ap.arrival_datetime,
        ep.end_station_name,
        ep.end_datetime
    from start_parts sp
    join end_parts ep on sp.route_id = ep.route_id
    join departure_parts dp on sp.route_id = dp.route_id
    join arrival_parts ap on sp.route_id = ap.route_id;
"""

SAFE_METHODS = 'GET', 'HEAD', 'OPTIONS', 'PATCH'
UNSAFE_METHODS = 'POST', 'PUT', 'DELETE'


RAILWAY_CARRIDGE_CHOICES = (
    ('Купе', 'Купе'),
    ('Плацкарт', 'Плацкарт'),
    ('СВ', 'СВ')
)


SEATING_IMAGES = {
    'Купе':'../static/tickets/img/kupe.jpg',
    'СВ':'../static/tickets/img/sv.jpg',
    'Плацкарт':'../static/tickets/img/platskart.jpg',
}

RAILWAY_CARRIDGE_PRICES = {
    'Купе':2500,
    'СВ':5000,
    'Плацкарт':1500,
}

####BOOST BANK
BOOST_URL = 'https://boostbank.ru/rest/bill/'
BOOST_HEADERS = {'Authorization': 'Token 0d48ba53e2d7a25e45dc65e6bd2e3a115fbceb28'}
BOOST_REDIRECT = 'https://boostbank.ru/payment/{id}'
BOOST_ACCOUNT = '8ac00fe9-95f2-4234-a3cf-941dff8189f7'
STATIC_THANKS = 'http://10.82.57.67:8000/succesessful'
BOOST_CALLBACK_URL = 'http://10.82.57.67:8000/rest/Ticket/{id}/'
BOOST_CALLBACK_HEADERS = {'Authorization': 'Token 8e96eaa3ff8510d4b5183742868ccb518971d040'}
