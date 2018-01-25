import re
import orodja

def zajemi_spletne_strani():
    osnovni_naslov = 'http://www.tate.org.uk/search'
    parametri = 'type=artwork&wdr=1900-1950'
    for stran in range(1, 238):
        naslov = '{}?{}&page={}'.format(osnovni_naslov, parametri, stran)
        ime_datoteke = 'tate/{:02}.html'.format(stran)
        orodja.shrani(naslov, ime_datoteke)

zajemi_spletne_strani()

regex_umetnina = re.compile(
    r'data-gtm-destination="page--artist">(?P<umetnik>.+?)</a></span>.*?'
    r'<span class=" card__title--artwork">(?P<naslov>.+?)</span>.*?'
    r'<span class="card__when--artwork-date">(?P<letnica>.+?)</span>.*?'
    r'<div class="card-footer">(?P<lokacija>.+?)'
    r'<span class="card__label card__label--acc-no">(?P<id>.+?)</span>.'
    ,
    flags=re.DOTALL)


def izloci_podatke_umetnin(imenik):
     umetnine = []
     for html_datoteka in orodja.datoteke(imenik):
          for umetnina in re.finditer(regex_umetnina, orodja.vsebina_datoteke(html_datoteka)):
               umetnine.append(pocisti_umetnino(umetnina))
     return umetnine

def pocisti_umetnino(umetnina):
    podatki = umetnina.groupdict()

    podatki['umetnik'] = podatki['umetnik']

    podatki['naslov'] = podatki['naslov']

    podatki['letnica'] = str(podatki['letnica'])

    if podatki['letnica'] == 'date not known':
        podatki['letnica'] = ('date not known', '', '', '')
    elif podatki['letnica'] == '20th Century':
        podatki['letnica'] = ('20th Century', '', '', '')
    elif podatki['letnica'] == '1921–c.23':
        podatki['letnica'] = ('1921–c.23', '1921', '1923', '')
    elif podatki['letnica'] == 'c.1945–c.1960–4, published c.1960–4':
        podatki['letnica'] = ('c.1945–c.1960–4', '1945', '1960', ', published c.1960–4')
    else:
        first = ''
        second = podatki['letnica']
        for i in range(len(podatki['letnica'])):
            if podatki['letnica'][i] in '0123456789':
                break
            else:
                first += podatki['letnica'][i]
                second = podatki['letnica'][i+1:]
        podatki['letnica'] = (first, second)

        leto = podatki['letnica'][1]
        if '–' in leto[:5]:
            leto = leto.split('–', 1)
            leto1 = leto[0]
            if len(leto[1]) < 2:
                leto2 = leto1[:3] + leto[1][0]
                leto = (leto1, leto2, '')
            elif leto[1][1] not in '0123456789':
                leto2 = leto1[:3] + leto[1][0]
                if len(leto[1]) < 3:
                    leto = (leto1, leto2, '')
                else:
                    leto = (leto1, leto2, leto[1][1:])
            elif leto[1][1] in '0123456789':
                leto2 = leto1[:2] + leto[1][:2]
                leto = (leto1, leto2, leto[1][2:])
        else:
            if len(podatki['letnica'][1]) == 4:
                leto = (podatki['letnica'][1], podatki['letnica'][1], '' )
            else:
                leto = (podatki['letnica'][1][:4], podatki['letnica'][1][:4], podatki['letnica'][1][4:] )
        podatki['letnica'] = (podatki['letnica'][0], leto[0], leto[1], leto[2])


    podatki['id'] = podatki['id']

    if r'</span>' not in podatki['lokacija']:
        podatki['lokacija'] = ('','')
    elif 'View by appointment' in podatki['lokacija']:
        podatki['lokacija'] = ('View by appointment','')
    else:
        new_string = ''
        m = podatki['lokacija']
        counter1 = 0
        counter2 = 0
        for i in range(len(m)):
            if m[i] == '>':
                counter2 += 1
                counter1 = counter2 + 1
            elif m[i] == '<':
                counter2 += 1
                new_string += m[counter1 - 1 :counter2 - 1] + '|'
            else:
                counter2 += 1
        lok = new_string.split('|')
        lokacije = []

        for i in range(len(lok)):
            if 'a' or 'e' or 'i' or 'o' or 'u' in  lok[i]:
                lokacije.append(lok[i])
        podatki['lokacija'] = (lokacije[3] + lokacije[4],  lokacije[7])



    return podatki


umetnine = izloci_podatke_umetnin('tate/')
orodja.zapisi_tabelo(umetnine, ['id', 'umetnik', 'letnica', 'naslov', 'lokacija'], 'tate/umetnine.csv')

print("Končano!")
