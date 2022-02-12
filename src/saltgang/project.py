import xdgappdirs

appname = "SuperApp"
appauthor = "Acme"

print(xdgappdirs.user_data_dir(appname, appauthor))
print(xdgappdirs.site_data_dir(appname, appauthor))
print(xdgappdirs.user_cache_dir(appname, appauthor))
print(xdgappdirs.user_config_dir(appname, appauthor))
print(xdgappdirs.user_log_dir(appname, appauthor))
