from sqlalchemy import create_engine
import numpy as np
import os


# def search_for(text, tfidf, svd, annoy, message_ids):
def search_for(text, embedder, annoy, message_ids):
    # vec = tfidf.transform([text])
    # vec = svd.transform(vec)
    vec = embedder.encode([text])
    vec = np.asarray(vec)

    m_ids = []
    for i in annoy.get_nns_by_vector(vec.ravel(), 10):
        m_ids.append(message_ids.message_id[i])

    db_string = "postgresql://postgres:postgres@postgres/postgres"
    db = create_engine(db_string)

    conn = db.raw_connection()
    cur = conn.cursor()

    links = []
    for i in m_ids:
        message_query = 'SELECT ts, channel_id, text FROM message WHERE message_id=%s'
        reply_query = 'SELECT ts, channel_id, thread_ts, text FROM reply WHERE message_id=%s'
        reply_query
        cur.execute(message_query, (i,))
        mres = cur.fetchone()
        if mres:
            print(mres[-1])
            link = f'{os.environ.get("SLACK_WORKSPACE_URL")}archives/{mres[1]}' + \
                f'/p{str(mres[0]).replace(".","").ljust(16, "0")}'
            links.append(link)
            continue
        cur.execute(reply_query, (i,))
        rres = cur.fetchone()
        if rres:
            print(rres[-1])
            link = f'{os.environ.get("SLACK_WORKSPACE_URL")}archives/{rres[1]}' + \
                f'/p{str(rres[0]).replace(".","").ljust(16, "0")}' + \
                f'?thread_ts={str(rres[2]).ljust(17,"0")}'
            links.append(link)

    #     link = cur.execute(f"SELECT * FROM message_links WHERE '{i}' == message_links.message_id;")
    #     link = cur.execute(f"SELECT * FROM cleaned WHERE '{i}' == cleaned.message_id;")
    #     links.append(link)

    # conn.commit()
    # conn.close()

    # return link
    return links
    # return m_ids
