import subprocess
import pyppeteer
import asyncio
import logging
import os
import os.path as op
from pyppeteer import launch
import tempfile

import tilesets.models as tm

import higlass_server.settings as hss

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponse, \
    HttpResponseNotFound, HttpResponseBadRequest

logger = logging.getLogger(__name__)

# import manage
# from bioblend.galaxy import objects
# from bioblend.galaxy import GalaxyInstance
# from bioblend.galaxy.histories import HistoryClient
# from bioblend.galaxy.datasets import DatasetClient
# import subprocess
# import argparse
# import re
# import os
# from string import Template
# import logging
# DEBUG = os.environ.get('DEBUG', "False").lower() == 'true'
# if DEBUG:
#     logging.basicConfig(level=logging.DEBUG)
# logging.getLogger("bioblend").setLevel(logging.CRITICAL)
# log = logging.getLogger()


# import django
# os.environ['DJANGO_SETTINGS_MODULE'] = "higlass_server.settings"
# django.setup()

# import tilesets.management.commands.ingest_tileset as ig
# from django.core.management import execute_from_command_line
# import clodius.cli.aggregate as cca
# import cooler.cli.zoomify as zoomify


# logger = logging.getLogger(__name__)

def galaxy(request):
    return "Helloworld"

def link(request):
    '''Generate a small page containing the metadata necessary for
    link unfurling by Slack or Twitter. The generated page will
    point to a screenshot of the rendered viewconf. The page will automatically
    redirect to the rendering so that if anybody clicks on this link
    they'll be taken to an interactive higlass view.

    The viewconf to render should be specified with the d= html parameter.

    Args:
        request: The incoming http request.
    Returns:
        A response containing an html page with metadata
    '''
    # the uuid of the viewconf to render
    uuid = request.GET.get('d')

    if not uuid:
        # if there's no uuid specified, return an empty page
        return HttpResponseNotFound('<h1>No uuid specified</h1>')

    try:
        obj = tm.ViewConf.objects.get(uuid=uuid)
    except ObjectDoesNotExist:
        return HttpResponseNotFound('<h1>No such uuid</h1>')

    # the url for the thumnbail
    thumb_url=f'{request.scheme}://{request.get_host()}/thumbnail/?d={uuid}'

    # the page to redirect to for interactive explorations
    redirect_url=f'{request.scheme}://{request.get_host()}/app/?config={uuid}'

    # Simple html page. Not a template just for simplicity's sake.
    # If it becomes more complex, we can make it into a template.
    html = f"""<html>
<meta charset="utf-8">
<meta name="author" content="Peter Kerpedjiev, Fritz Lekschas, Nezar Abdennur, Nils Gehlenborg">
<meta name="description" content="Web-based visual exploration and comparison of Hi-C genome interaction maps and other genomic tracks">
<meta name="keywords" content="3D genome, genomics, genome browser, Hi-C, 4DN, matrix visualization, cooler, Peter Kerpedjiev, Fritz Lekschas, Nils Gehlenborg, Harvard Medical School, Department of Biomedical Informatics">
<meta itemprop="name" content="HiGlass">
<meta itemprop="description" content="Web-based visual exploration and comparison of Hi-C genome interaction maps and other genomic tracks">
<meta itemprop="image" content="{thumb_url}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@higlass_io">
<meta name="twitter:title" content="HiGlass">
<meta name="twitter:description" content="Web-based visual exploration and comparison of Hi-C genome interaction maps and other genomic tracks">
<meta name="twitter:creator" content="@flekschas"><meta name="twitter:image:src" content="{thumb_url}">
<meta property="og:title" content="HiGlass"/>
<meta property="og:description" content="Web-based visual exploration and comparison of Hi-C genome interaction maps and other genomic tracks"/>
<meta property="og:type" content="website"/><meta property="og:url" content="https://higlass.io"/>
<meta property="og:image" content="{thumb_url}"/>
<meta name="viewport" content="width=device-width,initial-scale=1,shrink-to-fit=no">
<meta name="theme-color" content="#0f5d92">
    <body></body>
    <script>
        window.location.replace("{redirect_url}");
    </script>
    </html>
    """

    return HttpResponse(html)

def thumbnail(request: HttpRequest):
    '''Retrieve a thumbnail for the viewconf specified by the d=
    parameter.

    Args:
        request: The incoming request.
    Returns:
        A response of either 404 if there's no uuid provided or an
        image containing a screenshot of the rendered viewconf with
        that uuid.
    '''
    uuid = request.GET.get('d')

    base_url = f'{request.scheme}://localhost/app/'

    if not uuid:
        return HttpResponseNotFound('<h1>No uuid specified</h1>')

    if '.' in uuid or '/' in uuid:
        # no funny business
        logger.warning('uuid contains . or /: %s', uuid)
        return HttpResponseBadRequest("uuid can't contain . or /")

    if not op.exists(hss.THUMBNAILS_ROOT):
        os.makedirs(hss.THUMBNAILS_ROOT)

    output_file = op.abspath(op.join(hss.THUMBNAILS_ROOT, uuid + ".png"))
    thumbnails_base = op.abspath(hss.THUMBNAILS_ROOT)

    if output_file.find(thumbnails_base) != 0:
        logger.warning('Thumbnail file is not in thumbnail_base: %s uuid: %s',
                     output_file, uuid)
        return HttpResponseBadRequest('Strange path')

    if not op.exists(output_file):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            screenshot(
                base_url,
                uuid,
                output_file))
        loop.close()
    new_loc = "/home/higlass/projects/data/higlass_image.png"
    shutil.copy(output_file, new_loc)
    gie.put(new_loc)

    with open(output_file, 'rb') as file:
        return HttpResponse(
            file.read(),
            content_type="image/jpeg")

async def screenshot(
    base_url: str,
    uuid: str,
    output_file: str
):
    '''Take a screenshot of a rendered viewconf.

    Args:
        base_url: The url to use for rendering the viewconf
        uuid: The uuid of the viewconf to render
        output_file: The location on the local filesystem to cache
            the thumbnail.
    Returns:
        Nothing, just stores the screenshot at the given location.
    '''
    browser = await launch(
        headless=True,
        args=['--no-sandbox'],
        handleSIGINT=False,
        handleSIGTERM=False,
        handleSIGHUP=False
    )
    url = f'{base_url}?config={uuid}'
    page = await browser.newPage()
    await page.goto(url, {
        'waitUntil': 'networkidle0',
    })
    await page.screenshot({'path': output_file})
    await browser.close()



# class higlass_upload:

#     def __init__(self, dataset, data_name, datatype, genome=None):
#         self.dataset = dataset
#         self.data_name = data_name
#         self.datatype = datatype
#         self.genome = genome

#     ## RETRIEVE DATA FROM GALAXY
#     def upload(self, reseponse, dataset_id):
#         '''Takes data from gie.get and moves it to correct location'''
#         info = galaxy_import(dataset_id)
#         oldloc = "/import/" + dataset_id
#         newloc = "/home/higlass/projects/data" + info[dataset_id][0] + info[dataset_id][2]
#         shutil.move(oldloc, newloc)
#         return newloc, info[dataset_id][1] #new file location and genome

#     def gie_get(self, dataset_id):
#         '''Retrieves data and metadata from galaxy'''
#         gie.get(dataset_id)
#         info = metadata_info(dataset_id)
#         return info

#     def _metadata_info(self, datasets_identifiers, identifier_type='hid', history_id=None):
#         '''Modified version of gie.get, returns metadata of dataset'''
#         history_id = history_id or os.environ['HISTORY_ID']
#         metadata = {}
#         # The object version of bioblend is to slow in retrieving all datasets from a history
#         # fallback to the non-object path
#         gi = get_galaxy_connection(history_id=history_id, obj=False)
#         file_path_all = []

#         if type(datasets_identifiers) is not list:
#             datasets_identifiers = [datasets_identifiers]

#         if identifier_type == "regex":
#             datasets_identifiers = find_matching_history_ids(datasets_identifiers)
#             identifier_type = "hid"


#         for dataset_id in datasets_identifiers:
#             file_path = '/import/%s' % dataset_id
#             log.debug('Downloading gx=%s history=%s dataset=%s', gi, history_id, dataset_id)
#             # Cache the file requests. E.g. in the example of someone doing something
#             # silly like a get() for a Galaxy file in a for-loop, wouldn't want to
#             # re-download every time and add that overhead.
#             if not os.path.exists(file_path):
#                 hc = HistoryClient(gi)
#                 dc = DatasetClient(gi)
#                 history = hc.show_history(history_id, contents=True)
#                 datasets = {ds[identifier_type]: ds['id'] for ds in history}
                
#                 #Return name, type and genome for each upload
#                 if identifier_type == 'hid':
#                     dataset_id = int(dataset_id)
#                 metadata[dataset_id] = [dc.show_dataset(datasets[1])['name'],dc.show_dataset(datasets[1])['metadata_dbkey'], dc.show_dataset(datasets[1])['file_ext']]
#         return metadata

#     def genome_loaded(self):
#         '''Looks to see if chromosome size data has been uploaded, or if it's available in negspy if not'''
#         with open("/home/higlass/projects/datatypes.txt", 'r') as t, open("/home/higlass/projects/uploaded.txt", 'r+') as u:
#             genomedicts = t.read() +  "\n" + u.read()
#             if self.genome in genomedicts:
#                 return "Already available"
#             else:
#                 u.write("\n")
#                 u.write(self.genome)
#                 return self._negspytest()

#     def _negspytest(self):
#         # Looks to see if genome is available in negspy directory"
#         genome_loc = "/home/higlass/projects/negspy/negspy/data/" + self.genome + "/chromInfo.txt"
#         if os.path.isfile(genome_loc):
#             try:
#                 ig.ingest(filetype = "chromsizes-tsv", datatype = "chromsizes", coordSystem = self.genome, filename = genome_loc)
#             except:
#                 ##print("Could not generate new coordinate system properly")
#                 return "Could not generate new coordinate system properly"
#             return True
#         else:
#             ##print("Could not locate coordinate system for this file")
#             return "Could not locate coordinate system for this file"


#     def bedfile(self):
#         outstr = self.file_loc + ".galaxy"
#         cca._bedfile(self.file_loc, outstr, self.genome, None, False, None, 100, 1024, None, None, 0)
#         ig.ingest(filename = outstr, filetype = "beddb", datatype = "bedlike", coordSystem = self.genome)
#         return True