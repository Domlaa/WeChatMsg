import sys
from app.DataBase import micro_msg_db
from app.analysis.db_bootstrap import init_local_db

if __name__ == '__main__':
    init_local_db()
    contacts = micro_msg_db.get_contact()
    from app.DataBase.hard_link import decodeExtraBuf

    if contacts is None:
        print(f"contacts is none")
        sys.exit()
    print(f"contacts size: {len(contacts)}")
    group = 0
    s = {'wxid_ixcpa7s2p56622', 'wxid_h0k2lodk6p3e22', 'wxid_k99bxmw4fol222', 'wxid_hpdxs30hqzlp21', 'wxid_e6fx64m39uyg21', 'wxid_93olvr3l7dhv22'}
    for contact in contacts:
        wxid = contact[0]
        if contact[0] in s:
            print(contact[:7])
            buf = contact[9]
            info = decodeExtraBuf(buf)
            print(info)
        if wxid.__contains__('@chatroom'):
            remark = contact[3]
            nick_name = contact[4]
            print(f"find group {nick_name} id:{wxid}")
            group += 1
    print(f"find group {group}")
