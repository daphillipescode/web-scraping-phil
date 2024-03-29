from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from datetime import datetime
import bs4
from selectolax.lexbor import LexborHTMLParser

from app.models import UnprocessUrls, Results, UrlsProcess, ResultsImages


def sign_in(request):
    if request.method == "POST":
        user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'),
                            request=request)

        if user is not None and user.is_staff and user.is_active:
            login(request, user)
            request.session['user_id'] = user.id

            return JsonResponse({'data': 'Success'})
        else:
            return JsonResponse({'msg': 'Invalid username and password.'})

    return render(request, 'sign_in.html')


@login_required
def home(request):
    page = request.GET.get('page', 1)
    try:
        context = {
            'data': Paginator(Results.objects.filter(~Q(description=None)).order_by('title'), 15).page(page)
        }
        return render(request, 'listing.html', context)
    except Exception as e:
        print(e)


@login_required
def view_listing(request, pk):
    results = Results.objects.filter(Q(id=pk) & ~Q(description=None)).first()
    context = {
        'data': results,
        'images': ResultsImages.objects.filter(result_id=results.id)
    }
    return render(request, 'view_listing.html', context)


@login_required
def edit_listing(request, pk):
    if request.method == "POST":
        Results.objects.filter(id=pk).update(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            price=request.POST.get('price'),
            baths=request.POST.get('baths'),
            beds=request.POST.get('beds'),
            sqft=request.POST.get('sqft'),
            property_type=request.POST.get('property_type'),
            type=request.POST.get('type'),
            sub_type=request.POST.get('sub_type'),
            style=request.POST.get('style'),
            lot_size=request.POST.get('lot_size'),
            lot_info=request.POST.get('lot_info'),
            parking_info=request.POST.get('parking_info'),
            postal_code=request.POST.get('postal_code'),
            association_fee=request.POST.get('association_fee'),
            phone=request.POST.get('phone'),
            mls_number=request.POST.get('mls_number'),
            status=request.POST.get('status'),
        )

        return JsonResponse({'data': 'success', 'msg': 'You have successfully edited the listing.'})
    context = {
        'data': Results.objects.filter(id=pk).first(),
        'images': ResultsImages.objects.filter(result_id=pk)
    }
    return render(request, 'edit_listing.html', context)


@login_required
def unprocess_urls(request):
    try:
        urls = UnprocessUrls.objects.filter(scrape=0)

        for row in urls:
            url = row.url

            req = Request(
                url=url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            webpage = urlopen(req).read()
            soup = LexborHTMLParser(webpage)

            wrapper = soup.css('div.listings')
            if wrapper:
                for w in wrapper:
                    if w.css_first('a'):
                        link = w.css_first('a').attributes['href']
                        check = UrlsProcess.objects.filter(url=link)

                        if not check:
                            print("https://www.point2homes.com{}".format(link))
                            UrlsProcess.objects.create(
                                url="https://www.point2homes.com{}".format(link),
                                scrape=0
                            )

            UnprocessUrls.objects.filter(id=row.id).update(scrape=1, date_scrape=datetime.now())

        context = {}
        return render(request, 'unprocess_urls.html', context)
    except Exception as e:
        print(e)


@login_required
def process_status(status):
    if status:
        if status.lower() == 'en vata':
            return 'On Sale'
        else:
            return status
    else:
        return None


@login_required
def process_urls(request):
    try:
        today = datetime.now()
        urls = UrlsProcess.objects.filter(scrape=False)
        title = None
        description = None
        price = None
        beds = None
        baths = None
        sqft = None
        property_type = None
        phone = None
        types = None
        sub_type = None
        style = None
        lot_size = None
        lot_info = None
        mls_number = None
        parking_info = None
        postal_code = None
        association_fee = None

        total_image = 0
        for row in urls:
            req = Request(
                url=row.url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            webpage = urlopen(req).read()
            soup = BeautifulSoup(webpage, 'lxml')
            title = soup.find('h3', class_='section-title').text if soup.find('h3', class_='section-title') else None
            description = soup.find('div', class_='description-text').text.strip().replace('\r', '') if soup.find('div', class_='description-text') else None

            status = soup.find('h2', class_='property-type').text.strip() if soup.find('h2', class_='property-type') else None

            price = soup.find('div', class_='price').span.text.replace('\n', '').replace(' ', '') if soup.find(
                'div', class_='price') else None
            beds = soup.find('li', class_='ic-beds').strong.text if soup.find('li', class_='ic-beds') else None
            baths = soup.find('li', class_='ic-baths').strong.text if soup.find('li', class_='ic-baths') else None
            sqft = soup.find('li', class_='ic-sqft').strong.text if soup.find('li', class_='ic-sqft') else None
            property_type = soup.find('li', class_='ic-proptype').text.replace('\n', '').replace(' ', '')
            phone = soup.find('li', class_='phone-cell').span.get('data-phone') if soup.find('li',
                                                                                             class_='phone-cell') else None
            details_charcs = soup.find('div', class_='details-charcs')
            if details_charcs:
                for i in details_charcs:
                    if i and type(i) is bs4.element.Tag:
                        if i.dt and i.dt.text == 'Type':
                            types = i.dd.text.replace('\n', '')
                        elif i.dt and i.dt.text == 'Sub-Type':
                            sub_type = i.dd.text.replace('\n', '')
                        elif i.dt and i.dt.text == 'Style':
                            style = i.dd.text
                        elif i.dt and i.dt.text == 'Lot Size':
                            lot_size = i.dd.text
                        elif i.dt and i.dt.text == 'Lot Info':
                            lot_info = i.dd.text
                        elif i.dt and i.dt.text == 'MLS Number':
                            mls_number = i.dd.text
                        elif i.dt and i.dt.text == 'Parking Info':
                            parking_info = i.dd.text
                        elif i.dt and i.dt.text == 'Postal Code':
                            postal_code = i.dd.text
                        elif i.dt and i.dt.text == 'Association Fee':
                            association_fee = i.dd.text

            status = process_status(status)
            check = Results.objects.filter(title=title, status=status)

            if check:
                check.update(
                    url=row, title=title, description=description, price=price,
                    beds=beds, baths=baths, sqft=sqft, property_type=property_type, phone=phone, type=types,
                    sub_type=sub_type, style=style, lot_size=lot_size, lot_info=lot_info,
                    mls_number=mls_number, parking_info=parking_info, postal_code=postal_code,
                    association_fee=association_fee, status=status
                )
            else:
                result = Results(url=row, title=title, description=description, price=price,
                                       beds=beds, baths=baths, sqft=sqft, property_type=property_type, phone=phone, type=types,
                                       sub_type=sub_type, style=style, lot_size=lot_size, lot_info=lot_info,
                                       mls_number=mls_number, parking_info=parking_info, postal_code=postal_code,
                                       association_fee=association_fee, status=status)
                result.save()

                image_links_text = soup.find('div', class_='property-metro-photos')
                if total_image <= 15:
                    if image_links_text:
                        for img in image_links_text.ul:
                            if type(img) is bs4.element.Tag:
                                print(result.id)
                                image = img.get('data-src')
                                ResultsImages.objects.create(
                                    result_id=result.id,
                                    image=image
                                )
                                total_image += 1

            print(row.id, status, description)

            title = None
            description = None
            price = None
            beds = None
            baths = None
            sqft = None
            property_type = None
            phone = None
            types = None
            sub_type = None
            style = None
            lot_size = None
            lot_info = None
            mls_number = None
            parking_info = None
            postal_code = None
            association_fee = None

            total_image = 0
            row.date_scrape = today
            row.scrape = True
            row.save()

        context = {}
        return render(request, 'process_urls.html', context)
    except Exception as e:
        print(e)