import flet as ft
import env_canada as envcan
import csv
import asyncio
import flet_easy as fteasy
import BlurWindow.blurWindow as blurwindow #i hate capital letters sorry
import flet_restyle
import json
import os
import winsdk.windows.devices.geolocation as gps
import winsdk.windows.ui.accessibility as winAccessibility
import datetime
import sys
import math

# envcan.ECWeather()
SiteList = []
print("open preferences...")
prefs = {"unit":"C","defaultST":None,"enableAlerts":True}
appdataLoc = os.getenv('APPDATA')

def loadPrefs():
    global prefs
    try:
        if sys.argv[0] == "newPrefs":
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

with open("site_list_towns_en.csv") as f:
    siteListCSV = csv.reader(f,delimiter=",")
    for i in siteListCSV:
        print(i)
        SiteList.append({"id":i[0],"name":i[1],"province":i[2],"location":(i[3],i[4])})
    SiteList = tuple(SiteList)

# print(envcan.ECWeather(station_id="NL/s0000280").site_list)

# s0000280 for testing (dw im not doxing myself st. johns is the bigest city in my province)
def updateWeather(st:str="NL/s0000280",coords=(0,0)) -> envcan.ECWeather:
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
                            #  bgcolor=ft.colors.with_opacity(0.5,ft.colors.WHITE),
                            #  color=ft.colors.with_opacity(0.5,ft.colors.WHITE),
                            #  overlay_color=ft.colors.TRANSPARENT,
                            #  surface_tint_color=ft.colors.TRANSPARENT)
def getLocation() -> tuple:
    async def getPosition():
        return await gps.Geolocator().get_geoposition_async(datetime.timedelta(minutes=30),datetime.timedelta(minutes=30))
    loc = asyncio.run(getPosition()).coordinate
    locCords = (loc.latitude,loc.longitude)
    return locCords
weather = updateWeather(coords=getLocation())
@app.page("/home")
def homePage(data: fteasy.Datasy):
    # envcan.ECWeather().site_list
    if data.page.banner: #show alert again
        if not data.page.banner.open:
            data.page.banner.open = True
    view = ft.View("/home",bgcolor=ft.colors.TRANSPARENT)
    
    
    
    # view.appbar = ft.AppBar(title=ft.Text(f"Weather in : {weather.metadata['location']}"),actions=[ft.IconButton(ft.icons.REFRESH,on_click= lambda _: data.go('/refresh'))])
    # view.vertical_alignment   = ft.MainAxisAlignment.CENTER
    # view.horizontal_alignment = ft.MainAxisAlignment.CENTER
    
    #all my homies hate radians
    # if not weather.conditions['wind_dir']['value'] in ["N","NE","E","SE","S","SW","W","NW"]:
    #     origWinDir = "?"
    #     windIcon = ft.icons.QUESTION_MARK
    #     print(f"not recognised: {weather.conditions['wind_dir']['value']}")
    # else:
    #     origWinDir = weather.conditions['wind_dir']['value']
    #     windIcon = ft.icons.ARROW_UPWARD
    # windDirection = [0,0.785398,1.5708,2.35619,3.14159,-2.35619,-1.5708,-0.785398,0][["N","NE","E","SE","S","SW","W","NW","?"].index(origWinDir)]
    
    origWinDir = weather.conditions['wind_dir']['value']
    windIcon = ft.icons.ARROW_UPWARD
    windDirection = math.radians(("N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW").index(origWinDir)*22.5)
    windName = {"N":"Northern","NNE":"North eastern","NE":"North eastern","ENE":"North eastern","E":"Eastern","ESE":"South eastern", "SE":"South eastern", "SSE":"South eastern","S":"South eastern","SSW":"South western","SW":"South western","WSW":"South western","W":"Western","WNW":"North western","NW":"North western","NNW":"North western"}[origWinDir] #big boi line
    
    if weather.alerts and (not data.page.banner) and prefs["enableAlerts"]:
        print(weather.alerts)
        warningsNum = len(weather.alerts['warnings']['value'])
        watchesNum  = len(weather.alerts['watches']['value'])
        if warningsNum > 1:
            data.page.banner = (
                ft.Banner(bgcolor=ft.colors.RED,
                        open= True,
                        leading=ft.Icon(ft.icons.WARNING,color=ft.colors.WHITE),
                        content=ft.Text(f"NOTICE: thare are currently {warningsNum} weather warning/watche(s) in your area"),
                        actions=[ft.ElevatedButton("info",on_click=lambda _: data.go("/ALERT"))])
            )
        elif watchesNum > 1:
            data.page.banner = (
                ft.Banner(bgcolor=ft.colors.YELLOW,
                        open= True,
                        leading=ft.Icon(ft.icons.WARNING,color=ft.colors.WHITE),
                        content=ft.Text(f"NOTICE: thares is currently {warningsNum} weather warnings/watches in your area"),
                        actions=[ft.ElevatedButton("info",on_click=lambda _: data.go("/ALERT"))])
            )
    colum = ft.Column([ft.Row([ft.TextButton(content=
                                            ft.Text(f"temp: ",size=24,style=buttonTheme),on_click=lambda _: data.go("/home/temp")),
                                            ft.Text(f"{weather.conditions['temperature']['value']}℃",size=24,color=ft.colors.WHITE),
                                            ft.Icon(ft.icons.ARROW_UPWARD,size=24,color=ft.colors.GREEN),
                                            ft.Text(weather.conditions['high_temp']['value'],size=24,color=ft.colors.GREEN),
                                            ft.Icon(ft.icons.ARROW_DOWNWARD,size=24,color=ft.colors.RED),
                                            ft.Text(weather.conditions['low_temp']['value'],size=24,color=ft.colors.RED)]),
                       ft.Row([ft.Icon(windIcon,rotate=windDirection),ft.Text(f"{windName} facing winds at {weather.conditions['wind_speed']['value']} km/h")])
                       ],expand=True,width=360)
    
    #weather display
    
    weatherThing = ft.Row([
        ft.Text("weather icon will be here"),
        ft.Column([
            
        ])
        ])
    # weatherThing.controls.append()
    
    
    
    #part whare stuffs added
    
    view.controls.append(
        ft.Container(weatherThing,bgcolor=ft.colors.with_opacity(0.2,ft.colors.WHITE),border_radius=10,padding=ft.Padding(5,2,5,2),
                     alignment=ft.alignment.top_right,
                     expand=2
                     )
        )
    
    view.controls.append(ft.Container(colum,bgcolor=ft.colors.with_opacity(0.2,ft.colors.AMBER),expand=5,border_radius=10,padding=ft.Padding(5,2,5,2)))
    
    #credits and settings
    
    bottomRow = ft.Row()
    #candada momten
    bottomRow.controls.append(ft.Container(
        ft.Row([ft.Text("Data Source: Environment and Climate Change Canada",color=ft.colors.BLACK),
                ft.IconButton(ft.icons.INFO,on_click= \
                    lambda _:(data.page.launch_url('https://weather.gc.ca/canada_e.html')),
                    icon_color=ft.colors.BLACK)]),
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
    
    
    return ft.View("/home/temp",
                   [ft.Column([
                        ft.Text(f"right now: {weather.conditions['temperature']['value']}℃",size=42),
                        ft.Text(f"today's high: {weather.conditions['high_temp']['value']}℃",size=32),
                        ft.Text(f"today's low: {weather.conditions['low_temp']['value']}℃",size=32)])
                        # sunImage
                   ],
                   appbar=ft.AppBar(title=ft.Text("tempeture"),bgcolor=ft.colors.BLUE_700,color=ft.colors.WHITE),
                   bgcolor=ft.colors.BLUE_700)

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
            margin=ft.Margin(5,5,5,5),
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
            margin=ft.Margin(5,5,5,5),
            border_radius=10
            ))
    
    controls.append(ft.Text(f"raw json: {weather.alerts}"))
    controls.append(ft.Text("dev note: mkae this page look better wtf was i thinking."))
    return ft.View("/ALERT",
                   controls,
                   appbar=ft.AppBar(title=ft.Text("IMPORTANT ALERTS")),
                   bgcolor=ft.colors.BLACK)

@app.page("/setting")
def setupPage(data: fteasy.Datasy):
    view = ft.View(
        appbar=ft.AppBar(title=ft.Text("Settings"),center_title=True)
    )
    print(prefs)
    def setPrefs(e):
        global prefs
        prefs["enableAlerts"] = switches[0].value
        savePrefs()
    switches = [ft.Switch(value=prefs["enableAlerts"])] #so i can make other code cleaner
    
    
    
    
    def mkSettingsContainer(name:str,switchID:int,color = ft.colors.RED_600) -> ft.Container:
        switches[switchID].on_change = setPrefs
        def boxPress():
            switches[switchID].value = not switches[switchID].value
            switches[switchID].update()
            setPrefs()
        return ft.Container(
                ft.Row([ft.Text(name),switches[switchID]],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=color,
                border_radius=5,
                padding=ft.Padding(8,8,8,8),
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=6,
                    offset=ft.Offset(0,3)
                ),
                ink=True,
                on_click=boxPress
                # padding=ft.Padding()
            )
    view.controls.append(mkSettingsContainer("Weather Alerts",0))
    
    return view

@app.config
def configApp(pg:ft.Page):
    config = flet_restyle.FletReStyleConfig()
    # config.background = ft.colors.BLACK
    pg.title = "Weather"
    
    config.theme = ft.Theme(ft.colors.RED)
    
    #dont ask
    config.custom_title_bar = False
    config.frameless = False
    flet_restyle.FletReStyle.apply_config(pg,config) #<- used just to blur background
    pg.window_frameless = False
    pg.window_title_bar_hidden = False
    


app.run()

# def main(page: ft.Page):
#     gps = plyer.facades.GPS()
#     weather = envcan.ECWeather(station_id="NL/s0000280")
    
#     page.add(ft.SafeArea(ft.Text("Hello, Flet!")))


# ft.app(main)
