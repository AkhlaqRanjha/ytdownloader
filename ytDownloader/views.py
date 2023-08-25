from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import StreamingHttpResponse
from pytube import YouTube, Playlist
import os
from wsgiref.util import FileWrapper
import shutil
from django.contrib import messages
from requests import request

# Create your views here.

def ytd(request):
	return render(request, 'ytd.html')

def get_progress(request, res):
    homedir = os.path.expanduser("~")
    video_path = homedir + '/Downloads/video.mp4'

    # calculate the progress based on the current and total file size
    current_size = os.path.getsize(video_path)
    total_size = streams.filter(res=res).first().filesize
    progress = int(current_size / total_size * 100)

    return JsonResponse({'progress': progress})


def download_page(request):
	global url
	url = request.GET.get('url')

	yt = YouTube(url)
	global streams
	streams = yt.streams

	res = []
	ores = []
	for i in streams:
		onlyres = i.resolution

		string = str(i.resolution) + ' ' + str(i.filesize_approx // 1048576) + 'mb'

		res.append(string)
		ores.append(onlyres)
	
	ores = list(dict.fromkeys(ores))

	try:
		for j in range(len(ores)):
			if ores[j] == None:
				ores.pop(j)

	except:
		pass

	for k in range(len(ores)):
		ores[k] = ores[k] + ' ' + str(streams.filter(res=ores[k]).first().filesize // 1048576) + 'mb'
	
	title = yt.title
	author = yt.author
	length = str(yt.length//60) + ' minutes'
	if length == 0:
		length = str(yt.length) + ' seconds'

	thumbnail = yt.thumbnail_url
	print(thumbnail)


	res = list(dict.fromkeys(res))

	return render(request, 'download.html', {
		'onlyres': ores,
		'res': res,
		'title': title,
		'author': author,
		'length': length,
		'thumbnail': thumbnail,
	})

def success(request, res):
	global url

	homedir = os.path.expanduser("~")

	dirs = homedir + '/Downloads/'
  
	yt = YouTube(url)
	title = yt.title
	print(title)
	res,b = res.split()
	size = streams.filter(res=res).first().filesize // 1048576
	print(size)
	if request.method == 'POST' and size < 900:
		
		
		streams.filter(res=res).first().download(output_path = dirs, filename = "video.mp4")
		file = FileWrapper(open(f'{dirs}/video.mp4', 'rb'))
		# path =  '/home/runner/youtube-video-downloader/downloads/video' + '.mp4'
		# o = dirs + title + '.mp4'
		response = HttpResponse(file, content_type = 'application/vnd.mp4')
		response['Content-Disposition'] = 'attachment; filename = "video.mp4"'
		os.remove(f'{dirs}/video.mp4')
		return response
		# return render(request, 'success.html')

	else:
		return render(request, 'error.html')


def about(request):
	return render(request, 'about.html')

def music(request):
	return render(request, 'music.html')

# def download_music(request):
# 	url = request.GET.get('url')
# 	yt = YouTube(url)
# 	title = yt.title

# 	stream = yt.streams.filter(only_audio=True).first()
# 	#size = stream.filesize

# 	homedir = os.path.expanduser("~")

# 	dirs = homedir + '/Downloads/'
# 	size = stream.filesize // 1048576
	
# 	#messages.success(request, 'The download has been started, do not close this page')
# 	if request.method == 'POST' and size < 900:	
# 		stream.download(output_path = dirs, filename = f"{title}.mp3")
# 		file = FileWrapper(open(f'{dirs}/{title}.mp3', 'rb'))
# 		# path =  '/home/runner/youtube-video-downloader/downloads/video' + '.mp4'
# 		# o = dirs + title + '.mp4'
# 		response = HttpResponse(file, content_type = 'audio.mp3')
# 		response['Content-Disposition'] = f'attachment; filename = "{title}.mp3"'
# 		os.remove(f'{dirs}/{title}.mp3')
# 		return response
	# return render(request, 'success.html')
	# else:
	# 	return render(request, 'error.html')


def mp3_page(request):
    global url
    url = request.GET.get('url')

    yt = YouTube(url)
    global streams
    streams = yt.streams

    formats = []

    for stream in streams.filter(only_audio=True):
        format = {
            'resolution': stream.abr,
            'filesize': stream.filesize_approx // 1048576,
            # 'extension': stream.extension,
            'download_url': '/success/?url={}&resolution={}'.format(url, stream.abr)
        }

        formats.append(format)

    title = yt.title
    author = yt.author
    length = str(yt.length // 60) + ' minutes'
    if yt.length // 60 == 0:
        length = str(yt.length) + ' seconds'

    thumbnail = yt.thumbnail_url

    return render(request, 'download.html', {
        'formats': formats,
        'title': title,
        'author': author,
        'length': length,
        'thumbnail': thumbnail,
    })


def mp3_success(request, res):
    global url

    homedir = os.path.expanduser("~")
    dirs = os.path.join(homedir, 'Downloads')

    yt = YouTube(url)
    title = yt.title
    res, b = res.split()
    size = yt.streams.filter(only_audio=True, abr=res).first().filesize // 1048576

    if request.method == 'POST' and size < 900:
        stream = yt.streams.filter(only_audio=True, abr=res).first()
        audio_path = stream.download(output_path=dirs, filename="audio.mp4")

        file_size = os.path.getsize(audio_path)

        def file_iterator(file_path, chunk_size=8192):
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

        response = StreamingHttpResponse(file_iterator(audio_path), content_type='audio/mp4')
        response['Content-Length'] = file_size
        response['Content-Disposition'] = 'attachment; filename="audio.mp4"'

        os.remove(audio_path)
        return response

    return render(request, 'error.html')


def playlist(request):

	url = request.GET.get('url')

	playlist = Playlist(url)
	title = playlist.title
	videos = playlist.videos

	homedir = os.path.expanduser("~")

	dirs = homedir + f'/Downloads'

	size = 0

	for i in videos:
		stream = i.streams.filter(only_audio=True).first()
		size += stream.filesize // 1048576

	#messages.success(request, 'The download has been started, do not close this page')
	if size < 900:
		for i in videos:
			name = i.title
			stream = i.streams.filter(only_audio=True).first()
			stream.download(output_path = f'{dirs}/{title}', filename = f"{name}.mp3")

		path = shutil.make_archive(title,'zip', f'{dirs}/{title}')

		file = FileWrapper(open(path, 'rb'))

		response = HttpResponse(file, content_type='application/force-download')
		response['Content-Disposition'] = f'attachment; filename = "{title}.zip"'
		os.remove(path)
		os.remove(f'{dirs}/{title}')
		return response

	else:
		return render(request, 'error.html')

def contact(request):
	return render(request, 'contact.html')