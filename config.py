# court code map
location = {
    100: "SF-C1",
    101: "SF-C2",
    2: "LG1-C1",
    3: "LG1-C2",
    4: "LG1-C3",
    5: "LG1-C4",
    79: "LG1-C5",
    80: "LG1-C6",
}

# data source config
data_config = {
    "alumni": {
        "FETCH_URL": (
            "https://w5.ab.ust.hk/msalum/api/app/fbs/facility-timeslots?"
            "facility_id={id}&"
            "start_date={startdate}&"
            "end_date={enddate}"
        ),
        "User-Agent": "",
        "Authorization": "",
    },
}

# slot time filter
time_filter = {
    "START": 9,
    "END": 22,
}

# notify config
notify_config = {
    "pushdeer": {
        "BASE_URL": (
            "https://api2.pushdeer.com/message/push?pushkey={token}&text={text}"
        )
    },
    "feishubot": {
        "BASE_URL": "https://open.feishu.cn/open-apis/bot/v2/hook/{token}",
        "HEADERS": "{'Content-Type': 'application/json; charset=utf-8'}",
    },
    "larkbot": {
        "BASE_URL": "https://open.larksuite.com/open-apis/bot/v2/hook/{token}",
        "HEADERS": "{'Content-Type': 'application/json; charset=utf-8'}",
    },
}
