class Config:
    DEBUG = False
    DB_HOST = '127.0.0.1'
    DB_PORT = 3306
    DB_NAME = 'alttprbot'
    DB_USER = 'username'
    DB_PASS = 'password'

    SRL_NICK = 'SahasrahTest'
    SRL_PASSWORD = 'password'

    baseurl='https://alttpr.com'
    seed_baseurl='https://s3.us-east-2.amazonaws.com/alttpr-patches'
    username=None
    password=None

    SpoilerLogLocal='/path/to/spoilerlogs'
    SpoilerLogUrlBase='https://sahasrahbot.synack.live/spoilers'

    TournamentServers=[]
    TournamentQualifierSheet='GSHEET_ID'

    Tournament = {
    }

    SgApiEndpoint = ''

    BontaMultiworldServers = []

    MultiworldRomBase = 'http://localhost'
    MultiworldHostBase = 'localhost'

    gsheet_api_oauth={}

    SB_TWITCH_TOKEN = "oauth:xxxxxxxxx"
    SB_TWITCH_CLIENT_ID = "xxxxxxxx"
    SB_TWITCH_NICK = "BotName"
    SB_TWITCH_PREFIX = "$"
    SB_TWITCH_CHANNELS = [
        "#yourchannel"
    ]
