from datetime import datetime
import random
import hmac
import hashlib
import requests
import pymysql
import uuid

# 接入用户信息
Client_Id = "d0886c2c7044442db9fc8c1b09e799f9"
Client_Secret = "0b4ba0414b4e4cec831cdaa55bb79652"
# Client_Id = "a1cb5f24c9be44139d4a7de4a37dff26"
# Client_Secret = "26d11658144d42f3992f6e11bcf2a659"
Tenant_Id = 30
# 测试环境
BASE_URL = "http://mis.rongcard.com"
# 测试环境数据库配置信息
DB_HOST = "47.97.52.109"
DB_PORT = 3306
DB_USER = "xinghong"
DB_PWD = "sdf@#@$21"
DB_NAME = "rcbp-tsm"


def get_client_id():
    """
    获取client_id
    :return: client_id
    """
    return Client_Id


def get_client_secret():
    """
    获取client_secret
    :return: client_secret
    """
    return Client_Secret


def get_timestamp():
    """
    获取17位时间戳
    :return: 17位时间戳
    """
    return datetime.now().strftime('%Y%m%d%H%M%S%f')[0:17]


def get_random():
    """
    获取6位随机数
    :return: 6位随机数
    """
    return random.randint(100000, 999999)


def get_signature(client_secret, timestamp, random_num):
    """
    计算签名
    :param client_secret: client_secret
    :param timestamp: 时间戳
    :param random_num: 随机数
    :return: 签名值
    """
    string_to_sign = timestamp + "\n" + str(random_num)
    signature = hmac.new(bytes(client_secret, 'utf-8'), bytes(string_to_sign, 'utf-8'), hashlib.sha256).hexdigest()
    return signature


def get_access_token():
    """
    获取access_token
    :return: access_token
    """
    timestamp = get_timestamp()
    random_num = get_random()
    signature = get_signature(Client_Secret, timestamp, random_num)
    url = '%s/auth/rc/token' % BASE_URL
    payload = {
        "clientId": Client_Id,
        "timestamp": timestamp,
        "random": random_num,
        "signature": signature
    }
    r = requests.post(url, params=payload).json()
    return r['access_token']


def add_access_info(name, code, whitelist_user):
    """
    通过http接口，新增一接入方
    :param name: 接入方名称
    :param code: 机构代码
    :param whitelist_user: 是否为白名单用户（0否，1是）
    :return: 请求结果
    """
    access_token = get_access_token()
    url = '%s/tsm-service/sei/accessInfo' % BASE_URL
    payload = {
        "name": name,
        "code": code,
        "whitelistUser": whitelist_user
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer %s" % access_token
    }
    requests.post(url, json=payload, headers=headers).json()


def mysql(func):
    """
    mysql装饰器
    :param func: 返回待执行SQL
    :return: 返回SQL执行结果
    """
    def wrapper(*args, **kw):
        db = pymysql.connect(DB_HOST, DB_USER, DB_PWD, DB_NAME, DB_PORT)
        cursor = db.cursor()
        result = func(*args, **kw)
        li = None
        try:
            cursor.execute(result[1])
            if result[0] == "SELECT":
                li = cursor.fetchall()
            else:
                db.commit()
        except Exception as e:
            if result[0] != "SELECT":
                db.rollback()
            print(e)
        finally:
            cursor.close()
            db.close()
        return li
    return wrapper


def get_32uuid():
    """
    获取32位uuid
    :return: 32位uuid
    """
    m = hashlib.md5()
    m.update(uuid.uuid1().hex.encode('utf-8'))
    return m.hexdigest()


@mysql
def get_access_info(code):
    """
    获取接入方信息
    :param code: 机构代码
    :return:
    """
    sql = 'SELECT * FROM access_info WHERE code = "%s" AND tenant_id = "%s"' % (code, Tenant_Id)
    return "SELECT", sql


@mysql
def insert_access_info(name, code, whitelist_user):
    """
    直接操作数据库，新增一接入方
    :param name: 接入方名称
    :param code: 机构代码
    :param whitelist_user: 是否为白名单用户（0否，1是）
    :return:
    """
    status = '1'
    client_id = get_32uuid()
    client_secret = get_32uuid()
    app_key = get_32uuid()
    app_secret = get_32uuid()
    sql = 'INSERT INTO access_info(code, name, whitelist_user, status, client_id, client_secret, \
          app_key, app_secret, tenant_id) VALUES("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % \
          (code, name, whitelist_user, status, client_id, client_secret, app_key, app_secret, Tenant_Id)
    return "INSERT", sql


@mysql
def del_access_info(code):
    """
    操作数据库，删除一接入方
    :param code: 机构代码
    :return:
    """
    sql = 'DELETE FROM access_info WHERE code = "%s" AND tenant_id = "%s"' % (code, Tenant_Id)
    return "DELETE", sql


@mysql
def truncate_table(table_name):
    """
    清空一张表
    :param table_name: 表名
    :return:
    """
    sql = 'TRUNCATE %s' % table_name
    return "TRUNCATE", sql


if __name__ == "__main__":
    print(get_access_token())
