import flet as ft
import env_canada as envcan
import csv
import asyncio
import flet_easy as fteasy
import BlurWindow.blurWindow as blurwindow #i hate capital letters sorry
import flet_restyle
import json
import os
import time
import winsdk.windows.devices.geolocation as gps
import winsdk.windows.ui.accessibility as winAccessibility
import accentcolordetect
import datetime
import sys
import math
import copy
import base64
import textwrap
import requests
import win32mica
from copy import deepcopy
from ctypes import windll #for mica
import ctypes

licenses = ("""none""",) # might use other open scource thingys

# envcan.ECWeather()
SiteList = []
print("open preferences...")                                             #theme mode [acrylic,mica,none]
prefs = {"unit":"C","defaultST":None,"enableAlerts":True,"iconTheme":"canada","themeMode":"acrylic","prefsVersion":0,"compactMode":False,"comfyMode":False}
installedData = {"version":0}
transparentStyleTheme = False
icons = {"canada":()}
print(sys.argv)
def getDefaultView() -> ft.View:
    defaultView = ft.View()
    defaultView.bgcolor = ft.colors.TRANSPARENT
    if prefs['themeMode'] == "opaque":
        defaultView.bgcolor = accentcolordetect.accent()[1]
    
    return defaultView

airQualityColours = [ft.colors.BLUE_300,ft.colors.BLUE_500,ft.colors.BLUE_700,ft.colors.YELLOW_500,ft.colors.YELLOW_700,ft.colors.YELLOW_900,ft.colors.RED_300,ft.colors.RED_500,ft.colors.RED_800,ft.colors.RED_ACCENT_700]
appdataLoc = os.getenv('APPDATA')
tempdataLoc= os.getenv('Temp')
print(f"appdata  @ {appdataLoc}")
print(f"tempdata @ {tempdataLoc}")

def createIcon(code:int,baseImg:ft.Image  =ft.Image(width=128),scale=1) -> ft.Image|ft.Icon:
    if code.__class__ == str:
        code = int(code)
    if not code:
        baseImg.src = "assets/icons/badiconNIC.png"
        baseImg.scale = 1
        baseImg.border_radius = 10
        baseImg.width = 96
    else:
        baseImg.scale = scale
        if prefs["iconTheme"] == "canada":
            baseImg.src = f"https://weather.gc.ca/weathericons/{str(code).zfill(2)}.gif"
        elif prefs["iconTheme"] == "fletM3":
            baseImg = ft.Icon(
                [ft.icons.SUNNY,ft.icons.CLOUD_OUTLINED,ft.icons.CLOUD_CIRCLE_OUTLINED,
                 ft.icons.CLOUD_CIRCLE,ft.icons.CLOUD_UPLOAD,ft.icons.CLOUD_DOWNLOAD,
                 ft.icons.WATER_DROP_OUTLINED,ft.icons.SUNNY_SNOWING,ft.icons.SUNNY_SNOWING,
                 ft.icons.THUNDERSTORM,ft.icons.CLOUD,ft.icons.CLOUDY_SNOWING,
                 ft.icons.WATER_DROP_OUTLINED,ft.icons.WATER_DROP,ft.icons.GRAIN,
                 ft.icons.CLOUDY_SNOWING,ft.icons.CLOUDY_SNOWING,ft.icons.SNOWING,
                 ft.icons.SNOWING,ft.icons.THUNDERSTORM,ft.icons.FOGGY,
                 ft.icons.FOGGY,ft.icons.CLOUD_CIRCLE_OUTLINED,ft.icons.DEHAZE,
                 ft.icons.FOGGY,ft.icons.WIND_POWER_OUTLINED,ft.icons.SNOWING,
                 ft.icons.GRAIN,ft.icons.WATER_DROP,ft.icons.MODE_NIGHT,
                 ft.icons.MODE_NIGHT_OUTLINED,ft.icons.NIGHTS_STAY_OUTLINED,ft.icons.NIGHTS_STAY,
                 ft.icons.CLOUD_UPLOAD,ft.icons.CLOUD_DOWNLOAD,ft.icons.WATER_DROP_OUTLINED,
                 ft.icons.SNOWING,ft.icons.THUNDERSTORM,ft.icons.WIND_POWER,
                 ft.icons.TORNADO_OUTLINED,ft.icons.TORNADO,ft.icons.WIND_POWER,
                 ft.icons.FIREPLACE,ft.icons.VOLCANO_OUTLINED,ft.icons.ELECTRIC_BOLT,
                 ft.icons.ELECTRIC_BOLT,ft.icons.STORM][code],size=128 if scale == 2 else None
            )
        else:
            baseImg.src = f"assets/icons/{prefs['iconTheme']}/{str(code).zfill(2)}.png"
            if prefs["iconTheme"] == "paint":
                baseImg.scale /= 2
        
    return baseImg

def loadPrefs():
    global prefs
    try:
        if "--newPrefs" in sys.argv:
            raise FileNotFoundError
        with open(f"{appdataLoc}/hugie999/weather/prefs.json") as f:
            prefs = json.load(f)
    except FileNotFoundError:
        print("make new prefs file...")
        try:
            os.mkdir(f"{appdataLoc}/hugie999")
            print("and directory!?!?!?!??")
        except FileExistsError:
            pass
        try:
            os.mkdir(f"{appdataLoc}/hugie999/weather")
            print("another directory 🙄")
        except FileExistsError:
            pass
        with open(f"{appdataLoc}/hugie999/weather/prefs.json","w") as f:
            json.dump(prefs,f)

def savePrefs():
    global prefs
    try:
        if sys.argv[0] == "newPrefs":
            raise FileNotFoundError
        with open(f"{appdataLoc}/hugie999/weather/prefs.json","w") as f:
            json.dump(prefs,f)
    except FileNotFoundError:
        print("make new prefs file...")
        try:
            os.mkdir(f"{appdataLoc}/hugie999")
            print("and directory!?!?!?!??")
        except FileExistsError:
            pass
        try:
            os.mkdir(f"{appdataLoc}/hugie999/weather")
            print("another directory 🙄")
        except FileExistsError:
            pass
        with open(f"{appdataLoc}/hugie999/weather/prefs.json","w") as f:
            json.dump(prefs,f)

try:
    loadPrefs()
except json.decoder.JSONDecodeError:
    print("make new prefs file")
    savePrefs()

try:
    os.stat(appdataLoc+"/hugie999/weather/CANDATA/sites_en.csv")
except FileNotFoundError:
    print("!!!DOWNLOAD SITE LIST!!!")
    #download https://dd.weather.gc.ca/citypage_weather/docs/site_list_towns_en.csv
    try:
        os.mkdir(appdataLoc+"/hugie999/weather/CANDATA")
    except FileExistsError:
        pass
    with open(appdataLoc+"/hugie999/weather/CANDATA/sites_en.csv","wb") as f:
        r = requests.get("https://dd.weather.gc.ca/citypage_weather/docs/site_list_towns_en.csv")
        f.write(r.content)
    print("done.")
with open(appdataLoc+"/hugie999/weather/CANDATA/sites_en.csv") as f:
    siteListCSV = csv.reader(f,delimiter=",")
    for i in siteListCSV:
        # print(i)
        SiteList.append({"id":i[0],"name":i[1],"province":i[2],"location":(i[3],i[4])})
    SiteList = tuple(SiteList)

# print(envcan.ECWeather(station_id="NL/s0000280").site_list)

# s0000280 for testing (dw im not doxing myself st. johns is the bigest city in my province)
def updateWeather(st:str="NL/s0000280",coords=(0,0)) -> envcan.ECWeather:
    print(f"station: '{st}'")
    if st:
        weather = envcan.ECWeather(station_id=st)
    elif coords:
        weather = envcan.ECWeather(coordinates=coords)
    else:
        raise ValueError
    asyncio.run(weather.update())
    print(weather.conditions)
    return weather
# print(weather.alerts)
# weather = updateWeather()

app = fteasy.FletEasy(route_init="/home")
buttonTheme = ft.ButtonStyle(elevation=0,side=
                             {
                                 ft.MaterialState.HOVERED:ft.BorderSide(5,ft.colors.WHITE),
                                 ft.MaterialState.DEFAULT:ft.BorderSide(0,ft.colors.TRANSPARENT)},
                             shape={ft.MaterialState.DEFAULT:ft.RoundedRectangleBorder(radius=0)},
                             animation_duration=100)
                            #  bgcolor=f-t.colors.with_opacity(0.5,ft.colors.WHITE),
                            #  color=ft.colors.with_opacity(0.5,ft.colors.WHITE),
                            #  overlay_color=ft.colors.TRANSPARENT,
                            #  surface_tint_color=ft.colors.TRANSPARENT)
def getLocation() -> tuple:
    async def getPosition():
        return await gps.Geolocator().get_geoposition_async(datetime.timedelta(minutes=30),datetime.timedelta(minutes=30))
    loc = asyncio.run(getPosition()).coordinate
    locCords = (loc.latitude,loc.longitude)
    return locCords

weather:envcan.ECWeather

if prefs["defaultST"]:
    weather = updateWeather(st= prefs["defaultST"])
else:
    weather = updateWeather(coords=getLocation())

def autoUpdateWeather():
    global weather
    if prefs["defaultST"]:
        weather = updateWeather(st= prefs["defaultST"])
    else:
        weather = updateWeather(coords=getLocation())

# print(getLocation())
# exit(1)

print(weather.conditions)
print("\n")

def genWindIcon(windDir:str|int = weather.conditions['wind_bearing']['value']) -> ft.Icon:
    print(f"windDir: {windDir}")
    try:
        origWinDir = windDir
        windIcon = ft.icons.ARROW_UPWARD
        if windDir.__class__ == int:
            windDirection = windDir
        else:
            if windDir[:2] == "VR":
                windIcon = ft.icons.QUESTION_MARK_OUTLINED
                windDirection = 0
            else:
                windDirection = math.radians(("N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW").index(origWinDir)*22.5)
    except KeyError:
        origWinDir = 0
        windIcon = ft.icons.ERROR_OUTLINE
        windDirection = 0
    return ft.Icon(windIcon,rotate=windDirection)

@app.page("/home",page_clear=True)
def homePage(data: fteasy.Datasy):
    print(transparentStyleTheme)
    # data.page.title = ""
    global weather
    print(weather.metadata)
    aqi = envcan.ECAirQuality(coordinates=getLocation())
    asyncio.run(aqi.update())
    print(aqi.__dict__)
    print(aqi.current)
    print(data.page.views)
    view = getDefaultView()
    view.route = "/home"
    appTitle = ft.Text(f"Current weather for {weather.metadata['location']} {weather.station_id[:2]} ({weather.metadata['station']})",max_lines=1,overflow=ft.TextOverflow.ELLIPSIS)
    view.appbar = ft.AppBar(
        title=appTitle,
        center_title=True,
        bgcolor=(ft.colors.TRANSPARENT if transparentStyleTheme else None),
        actions=[ft.ElevatedButton("Change location...",on_click=lambda _:data.go('/setting/setSTmanual')),
                 ft.IconButton(ft.icons.REFRESH,on_click= lambda _:[autoUpdateWeather(),data.go("/"), print('a')]),
                 ft.PopupMenuButton(items=[
                    ft.PopupMenuItem(icon=ft.icons.ABC,text="temp")
                ]
        )],
        leading=None,
        toolbar_height=40 if prefs["compactMode"] else 100
    )
    print(f"title size: {appTitle.spans}")
    if weather.conditions == {}:
        print("no conditions!")
        conditions = weather.daily_forecasts[0]
        isFullConditions = False
        print()
        print(conditions)
        print()
        
        # data.go("/errors/jsonempty")
        # return ft.View()
    else:
        isFullConditions = True
        conditions = weather.conditions
    # envcan.ECWeather().site_list
    if data.page.banner: #show alert again
        if not data.page.banner.open:
            data.page.banner.open = True
    if not isFullConditions:
        print(weather.station_id)
        view.controls.append(ft.Container(
            ft.Row([ft.Text(
                    f"couldn't get full conditions for station {weather.metadata['location']} ({weather.station_id})"+\
                        (" it may be um-manned try again in the morning" if time.localtime(time.time()).tm_hour in [21,22,23,0,1,2,3,4,5,6,7] else " try again later...")
                        ),
                    ft.ElevatedButton(text="Change station",on_click= lambda _: data.go("/setting/setSTmanual"))],
                   alignment=ft.MainAxisAlignment.CENTER),
            expand=1,bgcolor=ft.colors.with_opacity(0.5,ft.colors.RED),alignment=ft.alignment.center,border_radius=10,padding=ft.Padding(5,2,2,5)))
    print()
    print(weather.hourly_forecasts)
    print()
    print(weather.conditions)
    print()
    
    # view.appbar = ft.AppBar(title=ft.Text(f"Weather in : {weather.metadata['location']}"),actions=[ft.IconButton(ft.icons.REFRESH,on_click= lambda _: data.go('/refresh'))])
    # view.vertical_alignment   = ft.MainAxisAlignment.CENTER
    # view.horizontal_alignment = ft.MainAxisAlignment.CENTER
    
    #all my homies hate radians
    # if not conditions['wind_dir']['value'] in ["N","NE","E","SE","S","SW","W","NW"]:
    #     origWinDir = "?"
    #     windIcon = ft.icons.QUESTION_MARK
    #     print(f"not recognised: {conditions['wind_dir']['value']}")
    # else:
    #     origWinDir = conditions['wind_dir']['value']
    #     windIcon = ft.icons.ARROW_UPWARD
    # windDirection = [0,0.785398,1.5708,2.35619,3.14159,-2.35619,-1.5708,-0.785398,0][["N","NE","E","SE","S","SW","W","NW","?"].index(origWinDir)]
    
    if isFullConditions:
        try:
            origWinDir = conditions['wind_dir']['value']
            windIcon = ft.icons.ARROW_UPWARD
            windDirection = math.radians(("N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW").index(origWinDir)*22.5)
            windName = {"N":"Northern","NNE":"North eastern","NE":"North eastern","ENE":"North eastern","E":"Eastern","ESE":"South eastern", "SE":"South eastern", "SSE":"South eastern","S":"South eastern","SSW":"South western","SW":"South western","WSW":"South western","W":"Western","WNW":"North western","NW":"North western","NNW":"North western"}[origWinDir] #big boi line
        except KeyError:
            origWinDir = "N"
            windIcon = ft.icons.ERROR_OUTLINE
            windDirection = 0
            windName = "error"
    else:
        origWinDir = "N"
        windIcon = ft.icons.ERROR_OUTLINE
        windDirection = 0
        windName = "no conditions error"
    
    if weather.alerts and (not data.page.banner) and prefs["enableAlerts"]:
        print(weather.alerts)
        warningsNum   = len(weather.alerts['warnings']['value'])
        watchesNum    = len(weather.alerts['watches']['value'])
        advisoriesNum = len(weather.alerts['advisories']['value'])
        statementsNum = len(weather.alerts['statements']['value'])
        
        if warningsNum > 0:
            data.page.banner = (
                ft.Banner(bgcolor=ft.colors.RED,
                        open= True,
                        leading=ft.Icon(ft.icons.WARNING,color=ft.colors.WHITE),
                        content=ft.Text(f"NOTICE: thare are currently {warningsNum} weather warning(s) in your area"),
                        actions=[ft.ElevatedButton("info",on_click=lambda _: data.go("/ALERT"))])
            )
        elif watchesNum > 0:
            data.page.banner = (
                ft.Banner(bgcolor=ft.colors.YELLOW,
                        open= True,
                        leading=ft.Icon(ft.icons.WARNING,color=ft.colors.WHITE),
                        content=ft.Text(f"NOTICE: thares is currently {warningsNum} weather watch(es) in your area"),
                        actions=[ft.ElevatedButton("info",on_click=lambda _: data.go("/ALERT"))])
            )
        elif advisoriesNum > 0:
            data.page.banner = (
                ft.Banner(bgcolor=ft.colors.GREY_800,
                        open= True,
                        leading=ft.Icon(ft.icons.WARNING,color=ft.colors.WHITE),
                        content=ft.Text(f"NOTICE: thares is currently {advisoriesNum} weather advisorys in your area",color=ft.colors.WHITE),
                        actions=[ft.ElevatedButton("info",on_click=lambda _: data.go("/ALERT"))])
            )
        elif statementsNum > 0:
            data.page.banner = (
                ft.Banner(bgcolor=ft.colors.GREY_800,
                        open= True,
                        leading=ft.Icon(ft.icons.WARNING,color=ft.colors.WHITE),
                        content=ft.Text(f"NOTICE: thares is currently {statementsNum} special weather statments in your area",color=ft.colors.WHITE),
                        actions=[ft.ElevatedButton("info",on_click=lambda _: data.go("/ALERT"))])
            )
        else:
            data.page.banner = None
    elif not prefs["enableAlerts"]:
        data.page.banner = None
    
    row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_EVENLY)
    if isFullConditions:
        colum = ft.Column([ft.Row([ ft.Icon(ft.icons.THERMOSTAT),            
                                    ft.Text(f"temperature: ",size=24,style=buttonTheme),
                                    ft.Text(f"{conditions['temperature']['value']}℃",size=24,color=ft.colors.WHITE),
                                    ft.Icon(ft.icons.ARROW_UPWARD,size=24,color=ft.colors.GREEN),
                                    ft.Text(conditions['high_temp']['value'],size=24,color=ft.colors.GREEN),
                                    ft.Icon(ft.icons.ARROW_DOWNWARD,size=24,color=ft.colors.RED),
                                    ft.Text(conditions['low_temp']['value'],size=24,color=ft.colors.RED)]),
                        ft.Row([genWindIcon(),ft.Text(f"{windName} ({conditions['wind_bearing']['value']}°) facing winds at {conditions['wind_speed']['value']} km/h")])
                        ],expand=0.4)
        colum.controls.append(ft.Row([ft.Icon(ft.icons.BLUR_ON),ft.Text(f"Wind chill: {conditions['wind_chill']['value']}℃")]))
    else:
        colum = ft.Column([ft.Row([
            ft.TextButton(content=ft.Text(f"temperature: {conditions['temperature']}℃",size=24,color=ft.colors.WHITE))]),
                        ft.Row([ft.Icon(windIcon,rotate=windDirection),ft.Text(f"{windName}")])
                        ],expand=0.3)
    # colum.controls.append(ft.Row([ft.Icon(ft.icons.FLIP_TO_BACK,size=24),ft.Text("Yesterday's weather:",theme_style=ft.TextThemeStyle.HEADLINE_LARGE)]))
    
    #add this later
    # colum.controls.append(ft.ExpansionTile(
    #     title=ft.Row([ft.Icon(ft.icons.FLIP_TO_BACK,size=24),ft.Text("Yesterday's weather:")]),
    #     # title=ft.Text("a"),
    #     controls=[
    #         ft.ListTile(title=ft.Text("high/low temperature"),leading=ft.Icon(ft.icons.THERMOSTAT),subtitle=ft.Row([
    #          ft.Icon(ft.icons.ARROW_DOWNWARD)   
    #         ]))
        
    #     ],
    #     # expand=True,
    #     width= 360,
    #     maintain_state=True
    #     ))
    
    print(ft.ExpansionPanel)
    row.controls.append(colum)
    colum = ft.Column()
    if isFullConditions:
        
        colum = ft.Column([
            ft.Row([
                ft.Icon(ft.icons.WATER_DROP),
                ft.Text(f"Chance of percipitation: {str(conditions['pop']['value'])+'%' if conditions['pop']['value'] else 'Unknown'}")
                ]),
            ft.Row([
                ft.Icon(ft.icons.SUNNY),
                ft.Text(f"UV Index: {conditions['uv_index']['value']}")
                ])
            
            ],expand=0.3,width=360)
    row.controls.append(colum)
    #aqi data
    
    # aqi.current = 14
    aqiTheme = copy.deepcopy(data.page.theme)
    if aqi.current > 10:
        aqiTheme.color_scheme_seed = airQualityColours[9]
    else:
        aqiTheme.color_scheme_seed = airQualityColours[round(aqi.current)-1]
    aqiTheme.color_scheme = ft.ColorScheme(aqiTheme.color_scheme_seed)
    print(aqiTheme)
    colum.controls.append(ft.Container(
        ft.Column([
        ft.Row([
            ft.Icon(ft.icons.AIR),
            ft.Text(f"Air quality: {aqi.current} (messured at {aqi.metadata['location']})"),
        ]),
        ft.Row([ft.Icon(ft.icons.TAG_FACES_OUTLINED,color=airQualityColours[0]),ft.ProgressBar(value=aqi.current/10,expand=True),ft.Icon(ft.icons.MOOD_BAD_OUTLINED,color=airQualityColours[9])])
        ]),bgcolor=ft.colors.with_opacity(0.3,ft.colors.SECONDARY_CONTAINER),padding=ft.Padding(5,5,5,5),border_radius=10,theme=aqiTheme
        ,tooltip="The canadian AQI scale goes from 1 to 10+",ink=True,on_click= lambda _: data.go("/home/AQI")))
    
    
    #weather display
    # if prefs["iconTheme"] == "canada":
    weatherThing = ft.Row([
        # ft.Text("weather icon will be here"),
        createIcon(conditions["icon_code"]['value'],scale=2),
        ft.Column([
            ft.FilledTonalButton("7 day forcast",on_click=lambda _: data.go("/home/7cast"),width=175,tooltip="View the forcast fot the next 7 days"),
            ft.FilledTonalButton("Hourly forcast",on_click=lambda _: data.go("/home/Hcast"),width=175,tooltip="View the forcast for the next few hours"),
            ft.FilledTonalButton("Radar",on_click=lambda _: data.go("/home/Rcast"),width=175,disabled=True,tooltip="Coming soon!")
        ],spacing=4,alignment=ft.MainAxisAlignment.SPACE_EVENLY),
        ft.Text(conditions['text_summary']['value'] if isFullConditions else conditions['text_summary'],size=16,max_lines=5,width=300)
        ],alignment=ft.MainAxisAlignment.SPACE_AROUND)
    
    # weatherThing.controls.append(ft.TextButton("test",on_click=lambda _: data.go("/home/7cast")))
    
    # weatherThing.controls.append()
    
    
    
    #part whare stuffs added
    
    view.controls.append(
        ft.Container(weatherThing,bgcolor=ft.colors.with_opacity(0.2,ft.colors.WHITE),border_radius=10,padding=ft.Padding(5,5,5,5),
                     alignment=ft.alignment.center,
                     expand=4
                     )
        )
    
    view.controls.append(ft.Container(row,bgcolor=ft.colors.with_opacity(0.2,ft.colors.PRIMARY_CONTAINER),expand=5,border_radius=10,padding=ft.Padding(5,5,5,5),alignment=ft.alignment.center))
    
    #credits and settings
    
    bottomRow = ft.Row()
    #candada momten
    
    bottomRow.controls.append(ft.Container(
        ft.Row([ft.Text("Data Source: Environment and Climate Change Canada",color=ft.colors.BLACK),
                ft.IconButton(ft.icons.INFO,on_click= \
                    lambda _:(data.page.launch_url('https://weather.gc.ca/canada_e.html')),
                    icon_color=ft.colors.BLACK)
                # ft.Text(conditions['observationTime']['value'].strftime("observed at %H:%M on (%d/%m)"),color=ft.colors.BLACK)
                ]),
        alignment=ft.alignment.bottom_left,bgcolor=ft.colors.with_opacity(0.8,ft.colors.WHITE),border_radius=10,expand=True,padding=ft.Padding(5,5,5,5)))
    
    bottomRow.controls.append(ft.Container(ft.IconButton(ft.icons.SETTINGS,on_click=lambda _:data.go("/setting"),scale=1.6),alignment=ft.alignment.bottom_right,border_radius=10,padding=ft.Padding(5,5,5,5)))

    view.controls.append(bottomRow)
    return view
    # return ft.View()
    # return ft.View(
    #     route="/home",
    #     controls=[
    #         ft.FilledButton("aaaaaa",style=buttonTheme)
    #     ],
    #     bgcolor=ft.colors.with_opacity(0.5,ft.colors.TRANSPARENT)
    # )
    
@app.page("/home/temp")
def tempaturePage(data: fteasy.Datasy):
    
    temp = weather.conditions['temperature']['value']
    
    if temp < -30:
        colour = ft.colors.BLUE_900
    
    elif temp < -10:
        colour = ft.colors.BLUE_800
    elif temp < 0:
        colour = ft.colors.BLUE_700
    elif temp < 10:
        colour = ft.colors.BLUE_200
    elif temp < 20:
        colour = ft.colors.BLUE_300 
    
    # sunImage = ft.Container(ft.Image(src="assets/sun.png"),alignment=ft.alignment.bottom_right)
    view = getDefaultView()
    view.route = "/home/temp"
    view.controls = [ft.Column([
                        ft.Text(f"right now: {weather.conditions['temperature']['value']}℃",size=42),
                        ft.Text(f"today's high: {weather.conditions['high_temp']['value']}℃",size=32),
                        ft.Text(f"today's low: {weather.conditions['low_temp']['value']}℃",size=32)])
                        # sunImage
                   ]
    view.appbar = ft.AppBar(title=ft.Text("tempeture"),bgcolor=ft.colors.TRANSPARENT,center_title=True)
    
    return view
@app.page("/ALERT")
def warningsPage(data: fteasy.Datasy):
    
    data.page.banner.open = False
    # data.page.banner = None
    alertStyle = ft.TextStyle(size=24,
                              color=ft.colors.BLACK)
    controls = []
    
    if weather.alerts['warnings']['value']:
        warnings = []
        for i in weather.alerts['warnings']['value']:
            warnings.append(ft.Container(ft.Row([ft.Text(i['title'],style=alertStyle),
                                                 ft.Text(f" on : {i['date']}",style=alertStyle)])))
        controls.append(ft.Container(
            ft.Column([
                ft.Text(f"{len(weather.alerts['warnings']['value'])} weather warning(s)",size=32,style=alertStyle)
            ]+warnings
            ),bgcolor=ft.colors.WHITE,
            padding=ft.Padding(5,5,5,5),
            border_radius=10
            ))
    if weather.alerts['watches']['value']:
        warnings = []
        for i in weather.alerts['watches']['value']:
            warnings.append(ft.Container(ft.Row([ft.Text(i['title'],style=alertStyle),
                                                 ft.Text(f" on : {i['date']}",style=alertStyle)])))
        controls.append(ft.Container(
            ft.Column([
                ft.Text(f"{len(weather.alerts['watches']['value'])} weather warning(s)",size=32,style=alertStyle)
            ]+warnings
            ),bgcolor=ft.colors.WHITE,
            padding=ft.Padding(5,5,5,5),
            border_radius=10
            ))
    
    controls.append(ft.Text(f"raw json: {weather.alerts}"))
    controls.append(ft.Text("dev note: mkae this page look better wtf was i thinking."))
    
    view = getDefaultView()
    view.route = "/ALERT"
    view.controls = controls
    view.appbar = ft.AppBar(title=ft.Text("IMPORTANT ALERTS"),center_title=True)
    return view

@app.page("/errors/jsonempty",page_clear=True)
def jsonEmptyError(data: fteasy.Datasy):
    print("json empty")
    for i in weather.__dir__():
        print(f"{i}: ")
        print(weather.__getattribute__(i))
        print()
    # exit(1)
    return ft.View(controls=[ft.Text("error: got empty json for conditions ):")],appbar=ft.AppBar(title=ft.Text("ERROR!")))

@app.page("/home/7cast")
def sevenDayForcast(data: fteasy.Datasy):
    view = getDefaultView()
    view.route = "/home/7cast"
    view.controls=[ft.Text("Forcast for the next seven days...")]
    view.appbar=ft.AppBar(title=ft.Text("Forcast for the next seven days..."),bgcolor=ft.colors.TRANSPARENT,center_title=True)
    
    i:dict
    print()
    print(weather.daily_forecasts)
    for i in weather.daily_forecasts:
        print(i)
        view.controls.append(ft.Card(ft.Container(
            ft.Container( #soo many columns help )':
                    ft.Column([
                        
                        ft.Row([
                            createIcon(i['icon_code'],ft.Image()),
                            ft.Column([
                                ft.Text(i['period']),
                                ft.Text(i["text_summary"],size=12,width=500),
                                
                                ])
                        ]),
                        ft.Text(f"temp: {i['temperature']}℃")]
                    )
                    ,padding=ft.Padding(10,10,10,10),bgcolor=ft.colors.TRANSPARENT
                )
            ),color=data.page.theme.color_scheme.inverse_surface,expand=0.5))
    view.scroll = ft.ScrollMode.ADAPTIVE
    
    for i in data.page.theme.color_scheme.__dict__.values():
        print(i)
        view.controls.append(ft.Icon(ft.icons.CIRCLE,color=i))
        
    
    return view

@app.page("/home/Hcast")
def sevenDayForcast(data: fteasy.Datasy):
    view = getDefaultView()
    view.route = "/home/Hcast"
    view.controls=[ft.Text("Forcast for the next few hours...")]
    view.appbar=ft.AppBar(title=ft.Text("Forcast for the next few hours..."),bgcolor=ft.colors.TRANSPARENT,center_title=True)
    print()
    print(weather.hourly_forecasts)
    
    i:dict
    p:datetime.datetime
    for i in weather.hourly_forecasts:
        if i['wind_direction'][:2] == "VR":
            windText= ft.Text(f"winds at {i['wind_speed']} km/h")
        else:
            windText= ft.Text(f"{i['wind_direction']} facing winds at {i['wind_speed']} km/h")
        print(i)
        p = i['period']
        view.controls.append(ft.Card(ft.Container(
            ft.Container( #soo many columns help )':
                    ft.Column([
                        
                        ft.Row([
                            createIcon(i['icon_code'],ft.Image()),
                            ft.Column([
                                ft.Text(p.astimezone().strftime("%I:%M [%p] (%a %d)")),
                                ft.Text(i["condition"],size=12,width=500),
                                
                                ])
                        ]),
                        ft.Row([
                            ft.Row([ft.Icon(ft.icons.THERMOSTAT),ft.Text(f"temp: {i['temperature']}℃")]),
                            ft.Row([ft.Icon(ft.icons.WATER_DROP),ft.Text(f"{i['precip_probability']} chance of percipitation")]),
                            ft.Row([genWindIcon(i['wind_direction']),windText])])]
                    )
                    ,padding=ft.Padding(10,10,10,10),bgcolor=ft.colors.TRANSPARENT
                )
            ),color=ft.colors.with_opacity(0.5,data.page.theme.color_scheme.inverse_surface),expand=0.5))
    view.scroll = ft.ScrollMode.ADAPTIVE
        
    
    return view

@app.page("/home/Rcast")
def radarPage(data: fteasy.Datasy):
    view = getDefaultView()
    view.appbar = ft.AppBar()
    view.scroll = True
    radar = envcan.ECRadar(coordinates=getLocation())
    asyncio.run(radar.update())
    with open(tempdataLoc+"/HWeatherCAtempradar.gif","wb") as f:
        f.write(asyncio.run(radar.image))
    
    view.controls.append(ft.Image(src=tempdataLoc+"/HWeatherCAtempradar.gif"))
    view.controls.append(ft.Image(src_base64=base64.encodebytes(radar).decode().replace("\n","")))
    # print(radar.__dict__)
    return view

@app.page("/setting")
def setupPage(data: fteasy.Datasy):
    view = getDefaultView()
    view.appbar=ft.AppBar(title=ft.Text("Settings"),center_title=True,bgcolor=ft.colors.TRANSPARENT)
    
    print(prefs)
    def setPrefs(e=None):
        global prefs
        prefs["enableAlerts"] = switches[0].value
        if switches[1].value and switches[2].value:
            switches[1].value, switches[2].value = False,False
            switches[2].update()
            switches[1].update()
        else:
            prefs["compactMode"] = switches[1].value
            prefs["comfyMode"] = switches[2].value
            
        savePrefs()
    switches = [ft.Switch(value=prefs["enableAlerts"]),ft.Switch(value=prefs["compactMode"]),ft.Switch(value=prefs["comfyMode"])] #so i can make other code cleaner
    
    
    
    def mkSettingsContainer(name:str,switchID:int,color = ft.colors.PRIMARY_CONTAINER) -> ft.Container:
        switches[switchID].on_change = setPrefs
        def boxPress(e):
            switches[switchID].value = not switches[switchID].value
            switches[switchID].update()
            setPrefs()
        return ft.Container(
                ft.Row([ft.Text(name),switches[switchID]],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=color,
                border_radius=5,
                padding=ft.Padding(8,8,8,8),
                ink=True,
                on_click=boxPress
                ,disabled=switchID == 2
                # padding=ft.Padding()
            )
    
    view.controls.append(mkSettingsContainer("Weather Alerts",0))
    view.controls.append(mkSettingsContainer("Compact mode",1))
    view.controls.append(mkSettingsContainer("Comfy mode",2))
    
    def saveThemeDropdown(e:ft.ControlEvent):
        prefs["themeMode"] = e.data.lower()
        savePrefs()
    
    themeDropDown = ft.Dropdown(options=[ft.dropdown.Option("Acrylic"),
        ft.dropdown.Option("Mica"),
        ft.dropdown.Option("Tabbed"),
        ft.dropdown.Option("Opaque")],
        label="theme mode",
        on_change=saveThemeDropdown,
        value=prefs["themeMode"].title())
    view.controls.append(ft.Container(
            themeDropDown
        ,bgcolor=ft.colors.PRIMARY_CONTAINER,
        border_radius=5,
        padding=ft.Padding(8,8,8,8)
        ))
    def iconPickerSelect(e:ft.ControlEvent):
        print(e.control.value)
        prefs['iconTheme'] = e.control.value
        savePrefs()
        
    iconPicker = ft.TextField(
        label="icon set",
        on_submit=iconPickerSelect,
        value=prefs["iconTheme"])
    view.controls.append(ft.Container(
            iconPicker
        ,bgcolor=ft.colors.PRIMARY_CONTAINER,
        border_radius=5,
        padding=ft.Padding(8,8,8,8)
        ))
    
    view.controls.append(ft.Text(f"weather metadata: {weather.station_id}"))
    view.controls.append(ft.Text(f"window size: {data.page.window_width},{data.page.window_height}"))
    
    view.controls.append(ft.TextButton("debug icons",on_click=lambda _: data.go('/debug/icons')))
    # view.controls.append(mkBlankSettingsContainer("Application Theme",ft.RadioGroup()))
    
    # aboutSheet = ft.BottomSheet(
    #         ft.Column(
    #             [   ft.Text("Licenses and stuff",size=42),
    #                 ft.Text("Meteocons (v2.0)",size=32),ft.Text("uses mit license"),
    #                 ft.TextField(value=licenses[0],read_only=True,multiline=True),
    #                 ft.FilledButton("find it here!",on_click=lambda _:data.page.launch_url('https://github.com/basmilius/weather-icons'))],
    #             scroll=True
    #         ),
    #         show_drag_handle=True,
    #         is_scroll_controlled=True
    #     )
    
    # def aboutSheetOpen(e):
    #     aboutSheet.open = True
    #     aboutSheet.update()
    
    # view.controls.append(aboutSheet)
    
    # view.controls.append(ft.Container(ft.FilledButton("Credits and open scource things used",on_click=aboutSheetOpen),alignment=ft.alignment.bottom_right))
    
    return view

@app.page("/debug/icons")
def iconsDebugPage(data: fteasy.Datasy):
    view = getDefaultView()
    view.appbar = ft.AppBar()
    view.scroll = True
    for i in (ft.icons.__dict__):
        print(i)
        view.controls.append(ft.Row([ft.Text(i),ft.Icon(i)]))
    
    return view

@app.page("/setting/setSTmanual")
def stationChangePage(data: fteasy.Datasy):
    view = getDefaultView()
    view.scroll = True
    view.appbar=ft.AppBar(title=ft.Text("set station..."),center_title=True)
    print(SiteList)
    def pickInputType(e:ft.ControlEvent):
        print(e.data)
        view.controls.clear()
        view.controls.append(inputTypePicker)
        view.controls.append(ft.Divider())
        if "man" in e.data:
            stationInput = ft.TextField(label="station id.")
            def saveST(e):
                prefs["defaultST"] = stationInput.value
                savePrefs()
                global weather
                weather = updateWeather(st=prefs["defaultST"])
                data.go("/home")
            
            view.controls.append(ft.Row([stationInput,ft.FilledButton("enter.",on_click=saveST)]))
        elif "ser" in e.data:
            def saveST(e:ft.ControlEvent):
                prefs["defaultST"] = e.control.data
                # print(e.data)
                # print(e.__dict__)
                # print(e.__class__)
                savePrefs()
                global weather
                weather = updateWeather(st=prefs["defaultST"])
                data.go("/home")
            def searchStations(e:ft.ControlEvent):
                term = stationInput.value
                print(e.__dict__)
                print(e.__class__)
                while len(view.controls) > 3:
                    view.controls.pop()
                matching = []
                for i in SiteList:
                    if term.lower() in i['name'].lower():
                        matching.append(i)
                # print(matching)
                view.controls.append(ft.Divider())
                for i in matching:
                    view.controls.append(ft.FilledButton(i['name'],expand=0.3,width=view.page.width,data=f"{i['province']}/{i['id']}",on_click=saveST))
                    print(f"{i['province']}/{i['id']}")
                view.update()
                # view.controls.append(ft.Row([stationInput,ft.IconButton(ft.icons.SEARCH,on_click=searchStations)]))
                
            stationInput = ft.TextField(hint_text="search stations...",expand=True,)
            view.controls.append(ft.Row([stationInput,ft.IconButton(ft.icons.SEARCH,on_click=searchStations)]))
        elif "aut" in e.data:
            view.controls.append(ft.Text("automatic selected.",theme_style=ft.TextTheme.body_large))
            prefs["defaultST"] = None
            # print(e.data)
            # print(e.__dict__)
            # print(e.__class__)
            savePrefs()
            global weather
            weather = updateWeather(updateWeather(coords=getLocation()))
            # data.go("/home")
        else:
            view.controls.append(ft.Text("pick one!"))
        view.update()
    inputTypePicker = ft.SegmentedButton([
        ft.Segment("ser",label=ft.Text("Search"),icon=ft.Icon(ft.icons.SEARCH),expand=True),
        ft.Segment("man",label=ft.Text("Manual"),icon=ft.Icon(ft.icons.ABC),expand=True),
        ft.Segment("aut",label=ft.Text("Automatic"),icon=ft.Icon(ft.icons.AUTO_MODE),expand=True)
        ],selected=[],allow_empty_selection=True,allow_multiple_selection=False,width=data.page.width,on_change=pickInputType)
    view.controls.append(inputTypePicker)
    view.controls.append(ft.Text("pick one"))
    
    
    return view
@app.config
def configApp(pg:ft.Page):
    global transparentStyleTheme
    pg.title = "Weather"
    pg.window_min_height = 500
    pg.window_min_width  = 800
    # pg.window_title_bar_hidden = True
    # pg.appbar = ft.AppBar(ft.Text("test"))
    pg.route
    print(pg.platform)
    print(accentcolordetect.accent())
    
    pg.window_to_front()
    HWND = windll.user32.GetForegroundWindow()
    
    
    # print(pg.on_route_change.)
    
    #delete this if porting
    assert pg.platform in [ft.PagePlatform.WINDOWS,ft.PagePlatform,"web"]
    if pg.platform != "web":
        pg.theme = ft.Theme(color_scheme_seed=accentcolordetect.accent()[1],
                            color_scheme=ft.ColorScheme(),
                            page_transitions=ft.PageTransitionsTheme(windows=ft.PageTransitionTheme.FADE_UPWARDS))
        pg.window_to_front()
        transparentStyleTheme = True
        if prefs["themeMode"] == "acrylic":
            config = flet_restyle.FletReStyleConfig()
            # config.background = ft.colors.BLACK
            
            
            config.theme = pg.theme
            print(accentcolordetect.accent()[1])
            #dont ask
            config.custom_title_bar = False
            config.frameless = False
            
            pg.window_to_front()
            flet_restyle.FletReStyle.apply_config(pg,config) #<- used just to blur background
            pg.window_frameless = False
            pg.window_title_bar_hidden = False
        elif prefs["themeMode"] == "mica":
            win32mica.ApplyMica(HWND,Theme=win32mica.MicaTheme.AUTO)
            print(accentcolordetect.accent())
        elif prefs["themeMode"] == "tabbed":
            win32mica.ApplyMica(HWND,Theme=win32mica.MicaTheme.AUTO,Style=win32mica.MicaStyle.ALT)
            print(accentcolordetect.accent())
        elif prefs["themeMode"] == "opaque":
            print("opaque")
            transparentStyleTheme = False
        else:
            raise ValueError(f"themeMode is not a proper value!\nit is: '{prefs['themeMode']}' when it should be one of [acrylic,tabbed,mica,opaque]!\nplease check the file at '{appdataLoc}\\hugie999\\weather\\prefs.json'")
            
    else:
        prefs["themeMode"] = "opaque"
    
    if prefs["compactMode"]:
        pg.theme.visual_density = ft.ThemeVisualDensity.COMPACT
    elif prefs["comfyMode"]:
        pg.theme.visual_density = ft.ThemeVisualDensity.COMFORTABLE
    else:
        pg.theme.visual_density = ft.ThemeVisualDensity.STANDARD
        
@app.page_404(page_clear=True)
def Page404(data:fteasy.Datasy):
    data.go("/home")
    return ft.View(controls=[ft.Text("a")])
@app.view
async def view(data: fteasy.Datasy):
    data.view.controls.append(ft.Text("yto"))
    
    return ft.View("/",[ft.Text("a")])


app.run()

# def main(page: ft.Page):
#     gps = plyer.facades.GPS()
#     weather = envcan.ECWeather(station_id="NL/s0000280")
    
#     page.add(ft.SafeArea(ft.Text("Hello, Flet!")))


# ft.app(main)
