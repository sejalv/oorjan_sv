from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from datetime import datetime #, timedelta
from haversine import haversine
import math, requests
from .models import Reference, LiveDC, InstallationKey
import utilities
#from django.core.urlresolvers import reverse
#from django.utils import timezone

# Create your views here.

@csrf_exempt
def post_livedc(request):
    try:
        installationkey = request.POST['installationkey']
        timestamp = datetime.strptime(request.POST['timestamp'], "%Y-%m-%d %H")
        dcpower = request.POST['dcpower']
    except KeyError:
        return HttpResponse(status=400,
                            content="Invalid request param. Input Must be a valid 'installationkey', 'timestamp' and 'dcpower'.")
    except ValueError:
        return HttpResponse(status=400, content="timestamp must be of format %Y-%m-%d %H")

    try:
        installation = InstallationKey.objects.get(installation_key=installationkey)
    except ObjectDoesNotExist:
        return HttpResponse(status=400, content="Invalid installation key")

    livedc, created = LiveDC.objects.update_or_create(installation_key=installation, timestamp=timestamp, #,dc_power=dcpower)
                                                      defaults={'dc_power': dcpower})
    return HttpResponse(status=201, content="Okay")

@csrf_exempt
def sim_livedc(request):
    try:
        installationkey = request.POST['installationkey']
        date = datetime.strptime(request.POST['date'], "%Y-%m-%d")
    except KeyError:
        return HttpResponse(status=400,
                            content="Invalid request param. Input Must be a valid 'installationkey', 'date'.")
    except ValueError:
        return HttpResponse(status=400, content="date must be of format %Y-%m-%d")

    try:
        installation_key = InstallationKey.objects.get(installation_key=installationkey)
    except ObjectDoesNotExist:
        return HttpResponse(status=400, content="Invalid installation key")

    for hour in range(0, 24):
        timestamp = date.replace(hour=hour, minute=00, second=00, microsecond=00)  # today.hour
        dcpower= utilities.genLiveDC_hourly(installationkey, hour)
        livedc, created = LiveDC.objects.update_or_create(installation_key=installation_key, timestamp=timestamp, #,dc_power=dcpower)
                                                      defaults={'dc_power': dcpower})

    return HttpResponse(status=201, content="Okay")

@csrf_exempt
def get_livedc(request):
    try:
        installationkey = request.GET['installationkey']
        date = datetime.strptime(request.GET['date'], "%Y-%m-%d")
    except KeyError:
        return HttpResponse(status=400,
                            content="Invalid request param. Input Must be a valid 'installationkey', 'date'.")
    except ValueError:
        return HttpResponse(status=400, content="date must be of format %Y-%m-%d")

    try:
        installation_key = InstallationKey.objects.get(installation_key=installationkey)
    except ObjectDoesNotExist:
        return HttpResponse(status=400, content="Invalid installation key")

    ldc = LiveDC.objects.filter(installation_key=installation_key, timestamp__date=date.date()).order_by('timestamp')
    content_heading="Live DC for Installation Key:"+installationkey+"<br> Date:"+str(date.date())+"<br><br>"
    content = ""
    for ld in ldc:
        content += str(ld.timestamp.hour)+":00:00 - "+str(ld.dc_power)+"<br>"
    return HttpResponse(status=200, content=content_heading+content if content else "Live Data not found for this IK/Date.<br>Please check parameters.")


@csrf_exempt
def get_performance(request):
    try:
        installationkey = request.GET['installationkey']
        date = datetime.strptime(request.GET['date'], "%d-%m-%Y")
    except KeyError:
        return HttpResponse(status=400,
                            content="Invalid request param. Input must be a valid 'installationkey', 'date'.")
    except ValueError:
        return HttpResponse(status=400, content="date must be of format %d-%m-%Y")

    try:
        installation_key = InstallationKey.objects.get(installation_key=installationkey)
    except ObjectDoesNotExist:
        return HttpResponse(status=400, content="Invalid installation key")

    msg = utilities.dailyPerformance(installationkey, date)
    content = "Live DC with low DC Power for InstallationKey: "+installationkey+"<br><br>"+msg if msg else "No data for this day or installation key"     #str.replace(msg, "<br>", "\n")
    return HttpResponse(status=200, content=content)


@csrf_exempt
def get_nearbyinstallationkey(request):
    try:
        lat = float(request.GET['lat'])
        lon = float(request.GET['long'])
        sc = float(request.GET['sc'])

    except (KeyError, TypeError):
        return HttpResponse(status=400, content="Invalid request param, input must be valid float lat-long-sc")

    """
    #refid = utilities.nearest_point(lat, long, sc)
    installationkey = InstallationKey.objects.filter(lat__range=(math.floor(lat)-0.01, math.ceil(lat)+0.01),
                                             long__range=(math.floor(lon)-0.01, math.ceil(lon)+0.01),
                                                system_capacity=sc)
    #for ik in installationkey:
    content=""
    """

    ik_id = utilities.nearest_point(lat, lon, sc)
    try:
        ik = InstallationKey.objects.get(installation_key=ik_id)
    except ObjectDoesNotExist:
        return HttpResponse(status=400, content="Installation key not found for these parameters")

    content = "IK ID: "+str(ik.installation_key)+"<br>Lat: "+str(ik.lat) +"<br>Lon: "+str(ik.long)\
                                                        +"<br>SC: "+str(ik.system_capacity)+"<br>"
    return HttpResponse(status=200, content=content)

@csrf_exempt
def post_installationkey(request):
    try:
        lat = float(request.POST['lat'])
        long = float(request.POST['long'])
        sc = float(request.POST['sc'])
    except (KeyError, TypeError):
        return HttpResponse(status=400, content="Invalid request param, input must be valid float lat-long-sc")
    try:
        ik = InstallationKey.objects.get(lat=lat, long=long, system_capacity=sc)
        return HttpResponse(status=400, content="An InstallationKey: {ik}, with given lat/lon/sc already exists!".format(ik=ik.installation_key))
    except:
        refid = utilities.nearest_point(lat, long, sc)
        print refid
        try:
            ref = Reference.objects.get(id=refid) if refid else None
            if haversine((lat, long), (ref.lat, ref.long)) <= 1:  # if ref object found in 1km radius
                installationkey, created = InstallationKey.objects.get_or_create(
                    lat=lat, long=long, system_capacity=sc, installation_id=ref)
            else:
                raise Exception
        except:
            refdc = utilities.getRefDC_API(lat, long, sc)
            if isinstance(refdc, str):
                return HttpResponse(status=400, content=refdc)
            else:
                ref, created = Reference.objects.update_or_create(lat=lat, long=long, system_capacity=sc,
                                                                  defaults={'dc': refdc})
                installationkey, created = InstallationKey.objects.get_or_create(
                                            lat=lat, long=long, system_capacity=sc, installation_id=ref)
        return HttpResponse(status=201, content="Okay <br>"+str(installationkey.installation_key))


@csrf_exempt
def get_reference(request):
    try:
        lat = float(request.GET['lat'])
        lon = float(request.GET['long'])
        sc = float(request.GET['sc'])
        date = datetime.strptime(request.GET['date'], "%d-%m-%Y")

    except (KeyError, TypeError):
        return HttpResponse(status=400, content="Invalid request param, input must be valid float lat-long-sc")

    day_of_year = date.timetuple().tm_yday
    """
    refs = Reference.objects.filter(lat__range=(math.floor(lat)-0.5, math.ceil(lat)+0.5),
                                             long__range=(math.floor(lon)-0.5, math.ceil(lon)+0.5),
                                                system_capacity=sc)
    """
    refid = utilities.nearest_point(lat, long, sc)
    ref = Reference.objects.get(id=refid)
    #content_body=""
    #for ref in refs:
    content_body = "Ref DC for Date:"+str(date.date())+"<br><br> Ref ID: "+str(ref.id)+"<br>Lat: "+str(ref.lat) +"<br>Lon: "\
                   +str(ref.long)+"<br>SC: "+str(ref.system_capacity)+"<br><br>"
    for hr in range(24):
        content_body += str(hr) + ":00:00 - " + str(ref.dc[str(day_of_year-1)][hr]) + "<br>"

    return HttpResponse(status=200, content=content_body if content_body else "Appropriate Reference data not found.<br>Please adjust lat/long/sc parameters")

@csrf_exempt
def post_reference(request):
    try:
        lat = float(request.POST['lat'])
        long = float(request.POST['long'])
        system_capacity = request.POST['system_capacity']
    except (KeyError, ValueError, TypeError):
        return HttpResponse(status=400, content="Invalid request param. Input must be valid lat, long, system_capacity")

    refdc = utilities.getRefDC_API(lat, long, system_capacity)
    if isinstance(refdc, str):
        return HttpResponse(status=400, content=refdc)
    else:
        ref, created = Reference.objects.update_or_create(lat=lat, long=long, system_capacity=system_capacity, defaults={'dc':refdc})
                                                      #defaults={'metadata': metadata, 'dc':dc})
        return HttpResponse(status=201, content="Created Reference ID:"+str(ref.id))


