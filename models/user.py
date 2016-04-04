from datetime import datetime
from functions import *
import time
import hashlib
import os


def get_token():
    return hashlib.sha1(os.urandom(128)).hexdigest()


def get_password_hash(password, secret_key):
    password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
    password_hash = password_hash[:15] + str(secret_key) + password_hash[15:]
    password_hash = hashlib.md5(password_hash.encode('utf-8')).hexdigest()
    
    return password_hash


############
### User ###
############
class UserModel(object):
    secret_key = 'default'
    token_expire_time = 3600

    # -------- #
    # Get List #
    # -------- #
    @staticmethod
    def get_single(cursor, id):
        sql = "SELECT \
               `id`, \
               `name`, \
               `email`, \
               `active` \
               FROM `user` \
               WHERE `id` = $id"
        
        replace = dict(id=id)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        result = cursor.fetchone()

        return result

    # -------- #
    # Get List #
    # -------- #
    @staticmethod
    def get_list(cursor):
        sql = "SELECT \
               `id`, \
               `name`, \
               `email`, \
               `active` \
               FROM `user`"
        
        cursor.execute(sql)
        result = cursor.fetchall()

        return result

    # ------ #
    # Verify #
    # ------ #
    @staticmethod
    def verify(cursor, token):
        # Return {'type': False, 'value': 1} - not found
        # Return {'type': False, 'value': 2} - token expired
        # Return {'type': True, 'value': 1} - success
        # Return {'type': True, 'value': 2} - success and update token time

        sql = "SELECT \
               `id`, \
               `datetime` \
               FROM `user` \
               WHERE `token` = $token \
               AND `active` = '1' \
               LIMIT 1"

        replace = dict(token=token)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        result = cursor.fetchall()

        if len(result) > 0:
            current_datetime = datetime.now()
            token_datetime = result[0]['datetime']
            current_timestamp = time.mktime(current_datetime.timetuple())
            token_timestamp = time.mktime(token_datetime.timetuple())

            if token_timestamp + UserModel.token_expire_time < current_timestamp:
                return {'type': False, 'value': 2}

            if token_timestamp + (UserModel.token_expire_time / 2) < current_timestamp:
                current_datetime = datetime.now()

                sql = "UPDATE `user` SET \
                       `datetime` = $datetime\
                       WHERE `id` = $id"

                replace = dict(datetime=current_datetime,
                               id=result[0]['id'])

                sql = sql_replace(sql, replace)
                cursor.execute(sql)
                
                return {'type': True, 'value': 2}

            return {'type': True, 'value': 1}

        return {'type': False, 'value': 1}

    # ----- #
    # Login #
    # ----- #
    @staticmethod
    def login(cursor, name_or_email, password):
        password_hash = get_password_hash(password, UserModel.secret_key)

        sql = "SELECT \
               `id`, \
               `name`, \
               `email`, \
               `token` \
               FROM `user` \
               WHERE (`name` = $name_or_email \
               OR `email` = $name_or_email) \
               AND `password` = $password \
               AND `active` = '1' \
               LIMIT 1"

        replace = dict(name_or_email=name_or_email,
                       password=password_hash)

        sql = sql_replace(sql, replace)

        cursor.execute(sql)
        result = cursor.fetchone()

        if result != None:
            token = get_token()
            current_datetime = datetime.now()

            sql = "UPDATE `user` SET \
                   `token` = $token, \
                   `datetime` = $datetime\
                   WHERE `id` = $id"

            replace = dict(token=token,
                           datetime=current_datetime,
                           id=result['id'])

            sql = sql_replace(sql, replace)
            cursor.execute(sql)
            result['token'] = str(token)

        return result

    # ----------- #
    # Insert Data #
    # ----------- #
    @staticmethod
    def create(cursor, data):
        # Return {'type': 'error', 'value': 1} - name exists
        # Return {'type': 'error', 'value': 2} - email exists
        # Return {'type': 'error', 'value': None} - error
        # Return {'type': 'success', 'value': <id:int>} - success

        sql = "SELECT \
               `name`, \
               `email` \
               FROM `user` \
               WHERE `name` = $name \
               OR `email` = $email \
               LIMIT 1"

        replace = dict(name=str(data['name']),
                       email=str(data['email']))

        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        result = cursor.fetchone()

        if result != None:
            if result['name'].lower() == data['name'].lower():
                return {'type': 'error', 'value': 1}

            if result['email'].lower() == data['email'].lower():
                return {'type': 'error', 'value': 2}

            return {'type': 'error', 'value': None}

        sql = "INSERT INTO `user` ( \
               `name`, \
               `email`, \
               `password`, \
               `active`, \
               `token`, \
               `datetime` \
               ) VALUES ( \
               $name, \
               $email, \
               $password, \
               $active, \
               $token, \
               $datetime \
               )"

        password_hash = get_password_hash(data['password'], UserModel.secret_key)
        token = get_token()
        current_datetime = datetime.now()

        replace = dict(name=data['name'],
                       email=data['email'],
                       password=password_hash,
                       active=data['active'],
                       token=token,
                       datetime=current_datetime)

        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        user_id = int(cursor.lastrowid)

        return {'type': 'success', 'value': user_id}

    # ----------- #
    # Update Data #
    # ----------- #
    @staticmethod
    def update(cursor, id, data):
        # Return {'type': 'error', 'value': 1} - name exists
        # Return {'type': 'error', 'value': 2} - email exists
        # Return {'type': 'error', 'value': None} - error
        # Return {'type': 'success', 'value': <id:int>} - success

        sql = "SELECT \
               `name`, \
               `email` \
               FROM `user` \
               WHERE (`name` = $name \
               OR `email` = $email) \
               AND `id` <> $id \
               LIMIT 1"

        replace = dict(name=data['name'],
                       email=data['email'],
                       id=id)

        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        result = cursor.fetchone()

        if result != None:
            if result['name'].lower() == data['name'].lower():
                return {'type': 'error', 'value': 1}

            if result['email'].lower() == data['email'].lower():
                return {'type': 'error', 'value': 2}

            return {'type': 'error', 'value': None}

        if data['password'] == None:
            sql = "UPDATE `user` SET \
                   `name` = $name, \
                   `email` = $email, \
                   `active` = $active \
                   WHERE `id` = $id"

            replace = dict(name=data['name'],
                           email=data['email'],
                           active=data['active'],
                           id=id)

            sql = sql_replace(sql, replace)
            cursor.execute(sql)
        else:
            sql = "UPDATE `user` SET \
                   `name` = $name, \
                   `email` = $email, \
                   `password` = $password, \
                   `active` = $active \
                   WHERE `id` = $id"

            password_hash = get_password_hash(data['password'], UserModel.secret_key)

            replace = dict(name=data['name'],
                           email=data['email'],
                           password=password_hash,
                           active=data['active'],
                           id=id)

            sql = sql_replace(sql, replace)
            cursor.execute(sql)

        user_id = int(id)

        return {'type': 'success', 'value': user_id}

    # ------------- #
    # Update Active #
    # ------------- #
    @staticmethod
    def update_active(cursor, id, active):
        result = None

        sql = "UPDATE `user` \
               SET `active` = $active \
               WHERE `id` = $id"

        replace = dict(id=id, active=active)
        sql = sql_replace(sql, replace)
        cursor.execute(sql)
        result = int(id)

        return result
