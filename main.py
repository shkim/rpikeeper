from telegram.ext import Updater, CommandHandler
import psutil
import time
import configparser
import subprocess

bot_token = None
tunnel_info = None

try:
    cparser = configparser.ConfigParser()
    if not cparser.read('config.ini'):
        print("Failed to read <config.ini> file")
        exit()
    section = cparser['DEFAULT']

    bot_token = section['BOT_TOKEN']
    tunnel_info = {
        'user': section['TARGET_HOST_USER'],
        'address': section['TARGET_HOST_ADDR'],
        'listen_port': section['TARGET_HOST_SSH_LISTEN_PORT'],
        'local_port': section['TARGET_HOST_LOCAL_TUNNEL_PORT'],
        'autossh_port': int(section['AUTOSSH_INTERNAL_PORT']),
    }
except:
    print("Invalid <config.ini> file.")
    raise SystemExit


def check_autossh():
    for cn in psutil.net_connections():
        if cn.status == 'LISTEN' and cn.laddr.port == tunnel_info['autossh_port']:
            return True
    return False

def seconds_elapsed():
    return time.time() - psutil.boot_time()

def run_autossh():
    cmdline = [
        'autossh',
        '-M', str(tunnel_info['autossh_port']),
        '-o', 'PubkeyAuthentication=yes',
        '-o', 'PasswordAuthentication=no',
        '-i', '/home/pi/.ssh/id_rsa',
        '-f', '-N', '-T', '-R',
        '{}:localhost:22'.format(tunnel_info['local_port']),
        '{}@{}'.format(tunnel_info['user'], tunnel_info['address']),
        '-p', tunnel_info['listen_port']
    ]
    #print(" ".join(cmdline))
    try:
        print(subprocess.call(cmdline))
        return True
    except Exception as ex:
        print(ex)
        return False


def hello(bot, update):
    update.message.reply_text('Hello {}'.format(update.message.from_user.first_name))


def handle_uptime(bot, update):
    update.message.reply_text('Uptime {} seconds'.format(seconds_elapsed()))


def handle_check_tunnel(bot, update):
    if check_autossh():
        update.message.reply_text('autossh connection exists.')
    else:
        update.message.reply_text('autossh connection not found.')


def handle_make_tunnel(bot, update):
    if check_autossh():
        update.message.reply_text('autossh connection already exists.')
    else:
        if run_autossh():
            update.message.reply_text('autossh executed.')
        else:
            update.message.reply_text('Failed to execute autossh.')


def start_bot():
    updater = Updater(bot_token)
    updater.dispatcher.add_handler(CommandHandler('hello', hello))
    updater.dispatcher.add_handler(CommandHandler('uptime', handle_uptime))
    updater.dispatcher.add_handler(CommandHandler('chktunnel', handle_check_tunnel))
    updater.dispatcher.add_handler(CommandHandler('mktunnel', handle_make_tunnel))
    updater.start_polling()
    print("Bot started.")
    updater.idle()

start_bot()
