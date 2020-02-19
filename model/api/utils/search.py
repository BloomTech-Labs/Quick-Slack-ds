from sqlalchemy import create_engine
import numpy as np
import os


def search_for(replies, tfidf, svd, tfidf_annoy, tfidf_m_ids, embedder, bert_annoy, bert_m_ids):
    # Get vectors
    tfidf_vec = tfidf.transform([replies])
    tfidf_vec = svd.transform(tfidf_vec)
    bert_vec = embedder.encode([replies])
    bert_vec = np.asarray(bert_vec)

    # Get ANN message ids
    m_ids = []
    query_list = bert_annoy.get_nns_by_vector(bert_vec.ravel(), 5, include_distances=True)
    for _, (a_index, distance) in enumerate(zip(query_list[0], query_list[1])):
        # Don't add ids that are too far away in hyperspace
        if distance < 1.13:
            m_ids.append(bert_m_ids.message_id[a_index])
        
    for i in tfidf_annoy.get_nns_by_vector(tfidf_vec.ravel(), 5):
        m_ids.append(tfidf_m_ids.message_id[i])
    
    # Remove duplicates
    m_ids = list(set(m_ids))

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

        link = cur.execute(f"SELECT * FROM message_links WHERE '{i}' == message_links.message_id;")
        link = cur.execute(f"SELECT * FROM cleaned WHERE '{i}' == cleaned.message_id;")
        links.append(link)

    conn.commit()
    conn.close()

    # return link
    return links
    # return m_ids
