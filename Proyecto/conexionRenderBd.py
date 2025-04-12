import psycopg2

def get_render_connection():

    try:
        return psycopg2.connect(
        host="dpg-cvrcoi15pdvs738eoum0-a.oregon-postgres.render.com",
        database="bd_ml601n_rouf",
        user="bd_ml601n_rouf_user",
        password="XCWvNgcZraiaoe4WPm9GEdbZq4UItoD7",
        port=5432,
        sslmode="require"
    )
    except Exception as e:
        return f"Error: {e}"