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
BOOST_URL = 'http://127.0.0.1:5000/rest/bill/'
BOOST_HEADERS = {'Authorization': 'Token f9421ebf48a19af28218ccea179bb5ae47a82af9'}
BOOST_REDIRECT = 'http://127.0.0.1:5000/payment/{id}'
BOOST_ACCOUNT = '00ab34de-41a3-4195-8761-d135bd57e5dd'
STATIC_THANKS = 'http://127.0.0.1:8000/succesessful'
BOOST_CALLBACK_URL = 'http://127.0.0.1:8000/rest/Ticket/{id}/'
BOOST_CALLBACK_HEADERS = {'Authorization': 'Token 9c103b950d4f16866ee35e00cf4c6a79af0a5209'}
