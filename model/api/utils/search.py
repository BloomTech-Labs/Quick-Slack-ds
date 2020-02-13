#from sqlalchemy import create_engine


def search_for(text, tfidf, svd, annoy, df):
    vec = tfidf.transform(text)
    vec = svd.transform(vec)

    m_ids = []
    for i in annoy.get_nns_by_vector(vec.ravel(), 10):
        m_ids.append(message_ids.message_id[i])

    # db_string = "postgresql://postgres:postgres@postgres/postgres"
    # db = create_engine(db_string)

    # conn = db.raw_connection()
    # cur = conn.cursor()

    # links = []
    # for i in m_ids:
        # link = cur.execute(f"SELECT * FROM message_links WHERE '{i}' == message_links.message_id;")
    #     link = cur.execute(f"SELECT * FROM cleaned WHERE '{i}' == cleaned.message_id;")
    #     links.append(link)

    # conn.commit()
    # conn.close()

    # return link
    return m_ids
