
"""
Script de collecte automatique Spotify/Deezer

"""

import requests
import pandas as pd
from datetime import datetime
import time
import os

# ==================== CONFIGURATION ====================
SPOTIFY_CLIENT_ID = '521adaf36b6948bb82d6c6f398f9004e'
SPOTIFY_CLIENT_SECRET = '11fcdc06df214181bfa8e8580c86126d'

# ==================== IDs SPOTIFY (324 artistes) ====================
SPOTIFY_IDS = [
    '7l6m2BySHwnjJuw22SXwh5',  # Limsa d'Aulnay
    '63fbQTZ9yW3SUsBRYcn1Wm',  # Julia Minkin
    '1gFiEIH4TiLrNeoq7rktTH',  # TR3NACRIA
    '2yTwZyGRSRDUjZNsLvIOW4',  # kulturr
    '1Wqloe5S1i29Ff7YiWg0x5',  # Natoxie
    '5r3DSRaJz8ckIw4XPH9Whd',  # Méne
    '4jF2P66DtNEficnixuIhKQ',  # marguerite
    '2swYfXhkzkb8s8djG6UjSm',  # Rousnam
    '06eMSN9Y5cS7EZX6nnkxpC',  # FRENCHGRL
    '51loVlVgRomkJwd04A6B1e',  # ZZ
    '46fYppQRc2dAeDAMnrVb6R',  # Ashvma
    '41Csk4RHbXp1jnMN4NWwOE',  # Mikado
    '7d1ctWXfrUvAe804Zld3Gy',  # Yoa
    '0RRp1XbMoTmW8zSWC1synA',  # Rambo goyard
    '29DEO5ubNTmLbFSEZDP2we',  # 1T1
    '5zCMyo4rRc63lqoXLKIcgv',  # Lushe
    '2VDWsiOnCzMSnxfinUYJkH',  # Bendo
    '6pg4S5KTCPiEBp0rSWsaI6',  # HMZ
    '2EnOL1ADehfBQB03ELa3QQ',  # Léman
    '7cLUwy0R7N8q1YSjHYZdrU',  # TRZ
    '3WUHUmukg1hiSrVCfCoSbF',  # 2 Mètres
    '5Hq9W3lm1N9KRCf35RBMab',  # Danyl
    '3mWqCmX0xuzBJN648XSBrE',  # DL91 Era
    '30SVAanrbFS6o0cIVDZ9ta',  # Thisizlondon
    '4vbZKiwmvbbW6onily9SJ5',  # Styleto
    '5bpoMhoeJ19sJSuELfgWMk',  # Missan
    '0utiBmutysHdb0zXFCLMT2',  # XVI
    '1h9kOJqZoCwgSbokQw6GsU',  # Lerizzle
    '5blvB6N3OACeH0gJL9BRqf',  # Ino Casablanca
    '60HWrpmSefhtMWCkghazzG',  # S2
    '0IUp0l21VlpoOz8525KfAJ',  # Mack H.D
    '36HOtWiV4nn0luNGSn2xAT',  # Jungle Jack
    '7pcG7za39JaUHalwqiuCt9',  # MPL
    '0VWHKHfSFwUhP0cuvVUfRN',  # WIXO & LA2S
    '1wRx48q25O8HPDTyNOUQ2k',  # 63OG
    '2jxihp917o7WCCEN3xZXww',  # Killa Predator
    '5hV6TRKQwmvIWKTlsob1z8',  # Bobbyezz
    '5Iib8YFyekylXZIqcVT1Qk',  # KGS
    '1Nm9adUt6D5iuhRgirlgF2',  # Huntrill
    '76aDH2U2OFw00wOWvhK6pk',  # Prod. 94
    '5bRjVnu5q4ySUkVYifxtGE',  # Vanou
    '6Tzkt668w24f7uHLTiq6tr',  # DVM
    '2D15WFlWJuCeEGC1LGss6X',  # Lisa Pariente
    '3TP2Ucsow6rW1s24aq9gb4',  # Lagui
    '15saPvefLxxtw3nvTOCUg0',  # Lille Saus
    '4yDo1iZ02sOpLsh1oGAAg9',  # Seth Sad
    '7FXX45sHqoQoCwqtG0ZV8H',  # Solda
    '2ktXCualVDXC8h7jNOuyoQ',  # La Plaie
    '2NtvkyG03ApOKPBj3TcQRt',  # Sheu
    '1J7b2Snol73xTmYILnCk1t',  # Eloïz
    '71x0OO2toFjXrMRcufL9tv',  # Poupie
    '1ESz23V2EMNGK2WhuAsTN9',  # Marlo
    '0jezfHhTNUwE6PwIC0IdXD',  # Jose Garcia
    '3i2AdhSP4YeSYY1m5JoUnK',  # Boumidjal X
    '0et1mZYLCSVBIBUY94B8Xn',  # Sokuu
    '41CySalxZ2GST1n69SqsZ1',  # Vayn
    '4acowSAiQXmdhs4DCgUQ0U',  # Ryflo
    '1sJDvsoQ9X10dibPnSSlsV',  # Waxx
    '7LBRgobZF7IvkSKljcuGDb',  # Lenaïg
    '5bvwbAyrx6Yk8oLHqOnJ9p',  # Fhin
    '1AmK5toq2JV8BT9tCkDFAa',  # Tazeboy
    '0k3C7u1fCchhNMHbcBy9xN',  # Kamelon Officiel
    '06iezeOUHGb86SaoYTyexg',  # ESTL
    '42ATKPvmj81n9JDOunFpqr',  # Jamso
    '3ZrvguSuVvHrFwbu9lFVe6',  # Zaka Lavista
    '6GGkEuZHoNpJsKYNZml2gL',  # THÉA
    '3uiTnIx5N6ZWAPkPb8GFC9',  # Lybro
    '1uN3byO6WUB2dSDg6XpsEw',  # Gaëlle
    '0Dr1nbwa1KW5wHYUCsrnAF',  # Metah
    '362uHPHfDmbmnXTy3w8ro4',  # 2zg
    '4ii7OZHtY3E4ndPm1MFMSR',  # PZK
    '3OFleM2K9wTLzf0wry6He3',  # Konieur
    '5resnspF60fUdkKmQHn8em',  # Clara Ysé
    '0TGeOStDbxqVi8UJdBQsEx',  # Zélie
    '6Miu2EYSCD74K7VzDYostC',  # Vernis Rouge
    '3glvSAS5Z6057HM9ov0HOt',  # Elle Valenci
    '4rKMthZmMbSiMdow1f1rBE',  # RDN
    '2K8TwF85tEXePefdOxPZTW',  # RDR
    '6LNDkL0VeHXi0fMuefWS1w',  # TVLM
    '1DcL22xdIWcdNa4ZHaXZjT',  # Bianca Costa
    '0C0OTAymY2bmqgYZ0WZCJI',  # Amaury
    '1DX6FDD9VMN2eJCmeFVbHi',  # Shayne
    '6CZhbpXpR3VJNQWFkwd2Ic',  # Noé Preszow
    '0M81CoQJFvfJH9BNnJvbQl',  # Almas
    '3Nmm3IacxsC92dEP0kWL3z',  # Tatiana Eva-Marie
    '3IrNp8pf0ugwmIEiGJCRse',  # Wamen
    '026nk210FPO26xMwpoew70',  # La Maîtrise de Saint Marc - LES CHORISTES
    '5BQdp2NlYGiwVgnCJB3gyX',  # MANARËM
    '0eFmnuvX7ZDCsnOesNifzb',  # Neaj
    '27y3Ud8v0SrHGx0uOYN34z',  # Maks
    '1q3qfgcLt7dhYNdWLEXgkX',  # Le D
    '7H3zHwjR1Wdxk6JVWV2a6c',  # Arèndi
    '2J0cbdwUlJkBYkQYIDDU5k',  # Tigre d'Eau Douce
    '6vorHF3qW6vODkQP51kGlk',  # DAYSY
    '0fEd76ZuO65826Q6ilZIuO',  # Lijay
    '1BC1J2L4JXtQG3JgtDVCrk',  # ZABUZA
    '1rBnd8KxDndiiiIyjOsFtw',  # Dika
    '7Kgv8CorcAKsG4of90vA5I',  # St Graal
    '6Rii9NJk3gtAOB1qnbTYPM',  # Danthology
    '3bM1MZ42q6lUJqHDaDwcKr',  # Marie-Flore
    '3PlSpnPQR0dZY50k3jfx7h',  # KELSON
    '19lhY4E6GLxH337OZLfOV4',  # Eu93ne
    '0nztDFQzc7SwCIGZnvDIJ7',  # Danilo
    '1id4EoPVo5qfzdP5gMf5U3',  # Kaf Malbar
    '5kKxz4PDHgrpIt8LX3PPiF',  # Jayel
    '5CnUroTELSGtd9HXmXOgaB',  # Afrobeats Central
    '28YuYWLmKm0vl1gb5cUIta',  # T-Jy
    '2JldlUF9gAWKZc1qNvjQpo',  # O - Olivier Marguerit
    '7Gd2a8LhB6hvrgFjuZMw9U',  # Emrod
    '7eFL3K5giCsAHXus03F7Cd',  # Molière l'opéra urbain
    '0avwZ2v9jOgVLB1IfimwdA',  # Coline Rio
    '2D2Wm1oAJrDRzXVzxkyBOE',  # Hulk
    '6KPfd2qfwePi6IM7RyQ3hd',  # LJK
    '79ydqO3TZ35NwkWtjyvugR',  # lille Caesar
    '6wknBTDOHIw2ZJNsCl2sx2',  # Mathu
    '4ltaLmNRwdD98CtEsot497',  # Esmée
    '082ELiDlIVdC1ovHXpWZHK',  # Diez
    '70BVuSoIusPEV52Fyi3RlK',  # Sp93
    '7EEdwUdhGRjusZNKBZ4kMU',  # Le Lounge Bar Français
    '5nrmuhl0AXvSLeoZgB3Tmr',  # Zaoui
    '0PL4oBFPdmDGLXFPaBpYcJ',  # Tample
    '7lOybRN1Qz34nPphHTHRHY',  # NIVK
    '7fGRdpiX855x7RBK8DjT1F',  # Braeker
    '7qYMSnsPIXmSMXfGVuCDwm',  # Fanny
    '2k0TTdszNNaFtbS7XdReiF',  # Fouzia
    '227ZhUtAhpZiTj8S80p1y5',  # 91
    '1VGFnvgAwxMlV8D729gs5I',  # RORI
    '0a0Pl9QiikzqYozn7qyooX',  # Félix Radu
    '0djUVWD4NWGZt9PLAlvYXj',  # YLR
    '3M1kdGJP7DlEBGPb1JtKJX',  # Traf
    '6uMAPLKPcylTmdl0F1T2HF',  # Sköne
    '2WSFLb1izcqFnU9KakhCnU',  # Janie
    '2BfjmShvoGPl4migLIun7a',  # Misié Sadik
    '2F7pKYW346RPkqdSH8NiGP',  # Atili
    '1WQU2IzBLUDasXeZBtSVA3',  # THK
    '5nnFJb2sF9qok7rGy1hg4d',  # F200
    '2Z55seSc1gT7BWnV0ElFNL',  # Nour
    '3OyQ9AeMFgwKFHUgBOISww',  # FLKN
    '1LmqhFAYA6BVhVx3kFrsZd',  # Lille
    '3mMx6lCCOvQZheRBZ3CTQs',  # TheFrenchKris
    '0NCfVJ4NDxaKUW8yV4lUlQ',  # Ebony
    '7lG3HWF81HrNSDVyK4zhuP',  # Xavier Polycarpe
    '4AcFhqecUgQOUNmdcdngEq',  # Jahlys
    '2UrTsnAc4CSukV44RC6PT6',  # LRB490
    '2MBvn4Y3ugNmUlWp1W65QL',  # ANAÏS MVA
    '4o3kvOwkHLKBgwcifYQUdF',  # Boris & Moris
    '0hO9TrLGquZn6cxbNqgpGl',  # Charles Ludig
    '4r9ruEx6tLz2x0WgtXVaoP',  # 94fatso
    '47RRhnkvrKrC6tm7fNYQTN',  # T913
    '7tJ1ZtOt4EOPyQnT8LE6rH',  # Allan
    '3xY67nlzCczbpUWrjCTdye',  # Lili Poe
    '1nn9NQhtKG0AfAjV5ZX8l4',  # L'Ordre Des Aventuriers
    '2xRBcpNYedlk5IhmIxfUqo',  # Micky Green
    '4PqSBgXKxQuqclKpwB6iuc',  # Blasé
    '1s1KgcCLx44NR59HUXy3ic',  # Karma 94
    '0aFrpBv0tkmDm9qFlXK2Gc',  # Kryssy
    '09X1kbjR9O2Cb3gdPvpgKG',  # Ève
    '5H4bQKIbNqf60vLbV9C0zq',  # Art-X
    '1IKjfLTjdQB5p8lqsTgJI1',  # 949PAYA$o
    '52CEzAtIDEJInO8yL0blFB',  # Jäde
    '3FDn3vsowXE4E7NNQn4fqq',  # Malter
    '1FmnkGJ5KDt1eCHJQVyAbk',  # Shake Shake Go
    '1S0pZbFHkQSJvvpzfIHXSS',  # SOROSORO
    '50odTEgNT8oNs9BrWD0kS4',  # Jazz douce musique d'ambiance
    '5MvTyp1ILPh1FZupAcFffI',  # Pompis
    '6dvyAgidTbcn9vJO1eWQ6y',  # Pep's
    '6UPRFx3Gnn5N67opROnwA5',  # Paris
    '7gdTFjXWEBzBtir4DGFzku',  # Lawskie
    '3JpL06DxPRePrKeYaRhKwH',  # Jumo
    '6CBm5KPNnurK4hFutVDIpz',  # SLK
    '0IKPfKkoKDbdQTKX0LCFZB',  # Mani Deïz
    '6a6yqBUTk6XxSsrstQIBQ6',  # Rakoon
    '6BGAhqSN3qEqlZRpMogAFN',  # Voleur pnz
    '1U2Bzt0bhkqHJj7L1WQdnB',  # Bruzer
    '0MKlq9NpviCizhTWbrC8KI',  # Cyclope l'Héritier
    '5TRkqLaI9iMFdFiqN1wAXa',  # Zitoune
    '142mBEMjSrFPCuDU0eS20r',  # Tookie2Beriz
    '1MbUL0JryiwgLoPNX8esk6',  # Blicassty
    '7DPzuksj4fnGIb4F9dVswN',  # Clou
    '0mAIVu2rtpW9TYcbp88wqn',  # sheng
    '6Sr0XZt2vowfPAzp9Mv1ck',  # Lille Fucker
    '20cVY12kekiJOzONmGOfyx',  # AZKA
    '1DaLT7Mgy04h833FKXKGO0',  # Lé Will & Deuspi
    '2aMYfhweGlfp6qj9r6OGUO',  # Vincent Peirani
    '4LiDDSfUo671okhAa6OSHY',  # Demon
    '0uFKA5yAa06BUDouOb1X8C',  # IN.94
    '1w8f71fNCVvZtiz4DLd7N5',  # Harley
    '2Le5krQdKYGiP5xUQnIHKN',  # Latop
    '1d38UPGn8PJ9XekumcIBha',  # wilsko
    '76CqcY9GUeWmu1sGbDDBwi',  # Rain 910
    '1dsLZMddSbqEnWNrXAZMr7',  # 949_creeper
    '0cfNKSR5Mcvh6jn8iPxcIT',  # Mec touché
    '57H433bibChwiap8GjXH34',  # John Alenca
    '6oay09Jpzlp3TKFbx7GBMY',  # DjeuhDjoah
    '0NLGp1poDBr1K4VVp3LVSL',  # L’Amerigo
    '7pJxy5TSBacc0UMMppaExZ',  # Rouquine
    '6R6tuqCxJRopO4bE8nfLGk',  # P.R2B
    '6Jnxg5O26hXfwfbRSMzVuB',  # Revnoir
    '3j5vom9KtuBUImiFXCOTP0',  # Doosko Niafo
    '5K45xjHulVclJDxJSakgmc',  # Green Money
    '4ASk9it8lXjK4KrkoFXPlN',  # Jahyanai King
    '2AfyzCxD2WTuEbV0XoZajq',  # Izzy93
    '2QKgfzDlgGJCv1hkfOovKH',  # Paris Richards
    '1ULJBOKjmOpRsRRHP1vc2X',  # tn_490
    '4vy2w9TDFpA1kcFCZRT5Ls',  # Ana Moreau
    '5RmuisBjJdDZ2OaLmWVMYu',  # Contrefaçon
    '4p5a11aaWH3aZrDuGrCWq6',  # Payaso915
    '4NbbicWEOV9MfkaTuZBUnh',  # Santos 912
    '5m9uhS0LyWhc5kFDWkeOjA',  # Saandia
    '475O928CVcLukJqBd4LPJ3',  # Sto
    '0KYFSSpklRwCSM31sHD4s6',  # Emile Parisien
    '3532P4f6wikwfG2uvxXRnQ',  # Dk2fois
    '1EkqwqtzsjxMYJZH73RFVM',  # ELISA ERKA
    '5JZqq78QDWcMNYjIRV81oF',  # Blam'S
    '5J65ukR6WWDkuRrqYa4Knl',  # ELOI
    '2ERWfqqrtdXicQJ9wcOONf',  # Revolver
    '2wGEnSqp6ZXg2LWGZF7mnQ',  # Dounia Jari
    '4AJBNggqryKH5Dy0xdaGDY',  # Cachemire
    '1AyxHP7cwxDjR5HxtxRo1C',  # Jazir
    '6PY5uOumDeaGto9AfoxCjh',  # Owen River
    '2VpYQkkjCohjSPskaQGyp0',  # West Bank Records
    '0kPQnkxRCKloZQfgXfrqQO',  # Rover
    '5KRLYv4JDKx5jvR2EOdw7a',  # Foé
    '4R15nQ1tIZGKIq7Z8BddVI',  # ASTERO-H
    '66rknd4NFEU7U2AK5cesjy',  # JLOW
    '0XVAP17xehWKLmcb0DhtbZ',  # Ici c'est Paris
    '1e9RDMOTSMtDV4ZkZTrZw4',  # 935
    '69NyHXNjgqvV4euhqZ36kH',  # Magoyond
    '6HB56S5tXln4QbDVbnd3h6',  # Rocket
    '1nmnKCdPXX14EBJWklwKTR',  # Casus Belli
    '1qvfwkeecGjBi5yJ1GBTNr',  # Shoota93
    '10zN9gAaRm3XKwtYzVZNql',  # New Jazz France
    '4ni1VfqTNIvsJKTDuiN64f',  # Merzhin
    '36buOdDVz6p3QbVatFi4iX',  # Rallye
    '2MOr3iEGgA7dQhYUsPBoTI',  # Sáez'93
    '5W38lYXVLIEfyTFBQKTfmX',  # Lulu Gainsbourg
    '1DEN3iWZL55rYkQCXVwkLz',  # King Luca
    '1MHoEOE8YNUmWKnqoEQS2Z',  # FRANKIE PARIS
    '690TcJftS8JgJI5iEsYEcU',  # Zonmai
    '2LvcgUerrHBC9tQd48v6kL',  # Les Petits Chanteurs D'Asnières
    '57dGH4c5aKHr46UJqCDEev',  # Simia
    '3dOo2vzOxx1HaSteQGb56s',  # Crie 930
    '67RmjpcaDCjcdKMiBuamuV',  # D4r
    '5O4IDbze1xrfs2zY8wLJ1H',  # Emlo
    '2fpKYZoJagtpX0aQ5xXiqq',  # King Daddy Yod
    '64jyZ8B8vuzf12J7NYAglD',  # DONI NA MA
    '5FM4iItgDdg47zRKbWnjzd',  # Lunar949
    '1quV4CgipPwybFtikATOBc',  # MC Salo
    '5mC0vGi5lOCqYs53SOojs4',  # Gabriel Paris
    '1ATrNccUrhiYSQ3B08VQrz',  # DAM
    '4O82966S46TGCDsAzRFlku',  # Jil Is Lucky
    '3g5QiiBmEWt5a3WaW1zArB',  # jaynbeats
    '685Gc0hObCotgZ7K8bE05K',  # Eloquence
    '3ED1AG2E67Epo3MBFVOFj9',  # Dolo Tonight
    '68uK8Nx6KBp8QZQi3YMU6L',  # Samat
    '1nqN4To65NIMSGsU0n8axa',  # Snoobie92
    '27zZxSk7AynBSC0XYiivLp',  # Les Amis D'ta Femme
    '3H7eNFfmHDrZoHoTfDJyGE',  # France Mpundu
    '5IFUbcd4w9UlVpsMNfY4FT',  # Poppy Fusée
    '1y1PK1PL2dgNh0TwQTpZMU',  # Le Réparateur
    '2RTeAMXtT5IZA4HndoFSNq',  # Humphrey
    '0lkiOp3vyxpN37Y6OCf9yO',  # NeoFX
    '0F2vt3PHYGZ8pSFBHZ0laC',  # Cheb Aymen Parisien
    '4MwF8qs0Uukh7VQdbVEcpP',  # Paris Paige
    '1dFiLNmRKzp1sA088KuwCw',  # Jasmïn
    '215tdyVWdDYOjufDKf6UJg',  # Warning
    '0sERWA25W58jwsWqspklGe',  # Adamé
    '0wHHtuNdjnmH9spIm2VrhR',  # Malo'
    '1tMIosPVEqpXGdD8JW1tIe',  # Thomas de Pourquery
    '2KUtIRV7tG4q4uyzHSkOqT',  # Terco92
    '6wUGiWb7FR3Cv39sELlp1U',  # Kasper 939
    '5ccC62eZo8vv2qTOTndIkn',  # $hiro
    '04Me6qNw3Z1CIqUWrkmF5B',  # LILLEN
    '7y4JSWyptLDbIWn5LOhydr',  # Haley James Scott
    '4jQd4K8fy9EuJJZErkbHts',  # Coco061
    '3xgVb12lTabQh3FnxXgjQk',  # PMD
    '6VUpGE6ErMWwqZGepBWc0D',  # Astral Bakers
    '6Y4IHXCDwWvuNBmdqTIUTz',  # Lille Pablo
    '1TtIkputhybiL64ttVwE1H',  # AfroBeats
    '37P7yznrsIGSfuGOzmmt26',  # AqME
    '0rBAjYzMBBP3u4LZLc1qwF',  # Afro S
    '4gkLBjl1hnfw2pmSZ1JNZl',  # Gabi
    '66xA2uEVOChiDTKdZd6hgV',  # SPORE
    '7JWxRPYnCGaZPh1L44NWtY',  # Oordaya
    '2FnT84XG3yKLIHEjheon9W',  # Nawel Ben Kraiem
    '0ZrPyHGPWRiOphFxml3rFO',  # Vibe
    '04YHyUbd7Ic47Zi2LtPzuv',  # Demusmaker
    '5wQ1ffwDHKe06PEKCIgLNG',  # David Castello-Lopes
    '6SOfR3vMDf9otrCMyzrdDn',  # Cabadzi
    '4KLjcYXXF6lORi2XOXAmz2',  # Grizzly 942
    '6rt9RysQUXJjzYXaIXdXu7',  # Paris Price
    '7wMBwaUmhrkuaq7vGWY8bt',  # KLN 93
    '4NOg3L0IrFUnGe6dhO1D2i',  # 94brizzy
    '1Bkcm42So5nKYkY5DEHbO2',  # Lillebittebock
    '7iogfxoFBRb7fwoxDIFJoG',  # Walk in Paris
    '1J65MRryoT7CWCesOe3nBb',  # La Phaze
    '6SlO9eMZZGEKIoYb6vlBkC',  # Johnny Montreuil
    '7Ix71RYt7HB9EHCJGjlk8J',  # Trigones Plus
    '43iw2eN2eQhF9GaouZCn1Q',  # Laskiiz
    '6kL9VJ0wAshNzlVZmSJZJN',  # Gus
    '3nul4CdUXaaA3QSHrduvtu',  # Esteban
    '0neByJeiLyO8TRikP9vXPV',  # Bagdad Rodeo
    '0qfeDvoajHGoVkmIW7fgra',  # 93PUNX
    '71EGGFm5wS2EwANKiWpKRE',  # Paris Saint Germain FanChants
    '41L28S3l8z3EZMledHcxHV',  # Bombes 2 Bal
    '6j2mAzLfu9ZMjd4rwCRjjn',  # Souli
    '2ublgvX7DlTU8ShDDslYVC',  # The S
    '77pl5wtTOGwF5FPUYUDEDz',  # rz92i
    '3KmJs3ery3PJQuQQ5FOllC',  # Lyan Paris
    '4BeUJGT638jeAuAvtm51oE',  # Carmen Maria Vega
    '0rXEHQAzDXBvblE2EZRBjL',  # Annie Lalalove
    '5Yz9TYi94Uup3otqHYUF5T',  # Mikeysem
    '7znBntfGatVV9Elt7uP8Bu',  # Schlaasss
    '3LTvQLZWuf9n2fOOq5dpG0',  # Jessica Marquez
    '1jEvmmt62aPniaH6j7py8S',  # Felipe
    '4sG5GeG7qK060XBll1R5ap',  # Une touche d'optimisme
    '0xOdtdbQkHKot7ODRxumLR',  # Aymen Parisien
    '5x6fEO7JyQd948Wvonm9xt',  # OPINEL 21
    '0LU6Sg6kRXbyjhzrw4xzxe',  # Power Struggle
    '7mTxA28IfHWWIuo2QKczgA',  # Pass Pass
    '0ddCzcAD0Echtycm6WsVcE',  # Secri IXV
    '1aC2EaDuaqmdG8HGLbjMf2',  # Davo 92
    '403x0fTWTfDHsV9PYkGFTe',  # Moderne
    '7Bwfit5Kgbtxwu5dnf2cVF',  # 92FLOWERS
]

# ==================== IDs DEEZER (191 artistes) ====================
DEEZER_IDS = [
    '8125697',  # Sisik
    '170886747',  # Styleto
    '12131',  # Rose
    '14633713',  # AM La Scampia
    '12086854',  # Maxence
    '12049',  # Darius
    '2398',  # Maze
    '13698817',  # Hervé
    '72417252',  # Chicaille Argenté
    '72597562',  # Foufa Torino
    '71363652',  # Youka
    '309680',  # Sam's
    '8557848',  # Kafon
    '12564376',  # Waxx
    '7639',  # Parabellum
    '12796111',  # S-Pion
    '343829',  # Marie-Flore
    '989667',  # Frànçois & The Atlas Mountains
    '8852364',  # Flora Fishbach
    '5376408',  # GAULOIS
    '9026872',  # Didou Parisien
    '136645872',  # No Limit
    '5098098',  # Adrian von Ziegler
    '128266712',  # Stéphane
    '1607',  # La Phaze
    '67727',  # Kennedy
    '96659',  # Philip
    '65148802',  # Disco Lines
    '504646',  # Le Bal des Enragés
    '1669858',  # Shlømo
    '4153477',  # Ева Польна
    '14310515',  # Terrenoire
    '1446067',  # Robi
    '11701147',  # Moka Boka
    '10267432',  # BLOWSOM
    '81160',  # Richard Grey
    '256226',  # Diego Pallavas
    '11066168',  # Anwar
    '13641021',  # Saint DX
    '14131735',  # Mathieu Des Longchamps
    '62082502',  # Sans Lactose
    '13311795',  # 22 Longs Riffs
    '56464392',  # Walls
    '99225682',  # Adamé
    '6901971',  # Zubi
    '11831069',  # Kedym
    '4456602',  # Alexia Gredy
    '74698',  # Balbino Medellin
    '136951462',  # Annie Lalalove
    '1711511',  # Bolivard
    '8582',  # Grandmaster Flash & The Furious Five
    '3267911',  # Cid
    '151908072',  # Walter Astral
    '340296',  # V13
    '4995016',  # Wolkenfrei
    '6066874',  # REYKO
    '13486',  # Hifi
    '4683064',  # JR O Crom
    '158683422',  # Searows
    '14329801',  # Meimuna
    '71238',  # Bouga
    '175066527',  # Lancelot
    '4018754',  # Labess
    '551',  # Spooks
    '5285689',  # Gorillaz featuring De La Soul
    '391466',  # Albany
    '5438687',  # Sault
    '72209',  # Tout Simplement Noir
    '9483070',  # Dina Ayada
    '5927653',  # MaMaMa
    '557542',  # Luar
    '79131832',  # Ralphie Choo
    '1400835',  # Squadra
    '122001252',  # Harley
    '154864891',  # Lilian Barbe
    '91132672',  # ILIONA
    '5280541',  # Sako (Chiens de Paille)
    '341448',  # Cheik Abderrahmane Soudaiss
    '13636759',  # Noé Preszow
    '260417',  # Alex Mills
    '4856051',  # 2zer
    '6607334',  # HEDIA
    '4822547',  # Dimitri Rougeul
    '7294142',  # KCIDY
    '285927',  # Index
    '1702852',  # Polocorp
    '149011',  # MBS
    '160336492',  # DO not DO
    '10098026',  # Huko
    '11539775',  # Nerlov
    '129700',  # Réciprok
    '89649',  # Sixième Sens
    '66705142',  # Nina Battisti
    '8673994',  # Palm Trees
    '13994675',  # Miel De Montagne
    '5973802',  # Kazy Lambist
    '2938511',  # Romare
    '2251',  # Le 3ème Œil
    '408682',  # Ouss & Riane
    '13719509',  # Tchiggy
    '11273910',  # Léa Paci
    '13942111',  # Tony Ann
    '9958710',  # Srno
    '273905',  # Snooky Pryor
    '205298',  # Nakk Mendosa
    '124952',  # Jalal El Hamdaoui
    '163940587',  # Mattyeux
    '95560',  # Leck
    '342163',  # Le réparateur
    '299044',  # Generationals
    '7210378',  # Emma Bale
    '67907232',  # Dry Cleaning
    '5564',  # Gaelle
    '13217707',  # chien noir
    '5145267',  # FRENSHIP
    '6579627',  # The Doug
    '70986422',  # Mariah the Scientist
    '4328434',  # Hollydays
    '13909493',  # P.R2B
    '5641260',  # Typh Barrow
    '1670514',  # Justin(e)
    '69076',  # Zesau
    '2215',  # Koma
    '10017',  # Dombrance
    '5435777',  # Zélie
    '445220',  # Jimmy Whoo
    '6760749',  # Camel Power Club
    '10339096',  # Pi Ja Ma
    '56048',  # Cheba Maria
    '395967',  # Parmalee
    '288658',  # Cate Le Bon
    '8973774',  # Ravyn Lenae
    '5841997',  # LE NOISEUR
    '4346644',  # Cween
    '164049927',  # Zaoui
    '5433412',  # Amel Zen
    '1196685',  # Poom
    '89094',  # Nakk
    '80440',  # Escobar Macson
    '4429709',  # Adrien Gallo
    '507710',  # Charlene Soraia
    '192002',  # Darcy
    '1243273',  # Adil El Miloudi
    '16801',  # La Clinique
    '50577082',  # 220 KID
    '156385',  # Solano
    '5852263',  # Lubiana
    '101621',  # Reda City 16
    '10493231',  # Master Sina
    '371669',  # Tony Romera
    '808276',  # Rai
    '14547813',  # Rusowsky
    '5957408',  # Fixpen Sill
    '5439694',  # Laurie Darmon
    '388718',  # Sheikh Abdul Basset Abdel Samad
    '102608',  # ALP
    '7077683',  # Bleu Toucan
    '80978422',  # Janie
    '7457468',  # Sen Senra
    '6469465',  # Max Styler
    '275677',  # Dabs
    '10154394',  # Clio
    '14277',  # Kiemsa
    '101969182',  # Sam Sauvage
    '3601941',  # Ajar
    '53742712',  # Dr. Yaro & La Folie
    '11488450',  # Ødyssey
    '13311053',  # St Graal
    '13733',  # KDD
    '136012742',  # VALORANT
    '7874592',  # Fouzi Torino
    '5387928',  # De Hofnar
    '1088905',  # Poolside
    '8681774',  # Antoine Elie
    '507886',  # Colt
    '77163',  # Clou
    '1690810',  # Jean Tonique
    '4459137',  # Сергей Трофимов
    '1593750',  # Laura Cahen
    '5701960',  # Léonie Pernet
    '1611138',  # Diva Faune
    '96110972',  # Rouquine
    '78200722',  # Johnny Jane
    '9305278',  # Soge Culebra
    '1453262',  # Low Deep T
    '14814377',  # Naestro
    '12231880',  # Coline Rio
    '1376656',  # Lulu Gainsbourg
    '345686',  # Sage
    '75964992',  # Magenta Club
    '1428115',  # Malo'
]

# ==================== FONCTIONS ====================

def get_spotify_token():
    """Obtenir le token d'accès Spotify"""
    
    # Lire depuis les variables d'environnement
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    # Vérifier que les credentials existent
    if not client_id or not client_secret:
        raise ValueError("SPOTIFY_CLIENT_ID et SPOTIFY_CLIENT_SECRET doivent être définis")
    
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    
    # Vérifier la réponse
    if auth_response.status_code != 200:
        print(f"Erreur d'authentification Spotify: {auth_response.status_code}")
        print(f"Réponse: {auth_response.text}")
        raise Exception("Échec de l'authentification Spotify")
    
    return auth_response.json()['access_token']


def collecter_spotify(artist_ids):
    """Collecter données depuis Spotify API"""
    print(f"\nCollecte Spotify de {len(artist_ids)} artistes...")
    
    token = get_spotify_token()
    if not token:
        print(" Impossible d'obtenir le token Spotify")
        return pd.DataFrame()
    
    headers = {'Authorization': f'Bearer {token}'}
    artists_data = []
    errors = []
    
    for idx, artist_id in enumerate(artist_ids, 1):
        print(f"  [{idx}/{len(artist_ids)}] ID: {artist_id[:8]}...", end=" ")
        
        try:
            response = requests.get(
                f'https://api.spotify.com/v1/artists/{artist_id}',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                artists_data.append({
                    'id_unique': f"{data['name']}_spotify",
                    'nom': data['name'],
                    'source': 'Spotify',
                    'followers': data['followers']['total'],
                    'popularity': data['popularity'],
                    'genre': ', '.join(data['genres'][:3]) if data['genres'] else 'Non spécifié',
                    'image_url': data['images'][0]['url'] if data['images'] else '',
                    'url_spotify': data['external_urls']['spotify'],
                    'date_collecte': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                print(f" {data['name']} ({data['followers']['total']:,} followers)")
                
            elif response.status_code == 404:
                print(f" Artiste non trouvé")
                errors.append((artist_id, "Non trouvé"))
            elif response.status_code == 429:
                print(f" Rate limit, attente 60s...")
                time.sleep(60)
                # Retry
                response = requests.get(
                    f'https://api.spotify.com/v1/artists/{artist_id}',
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    artists_data.append({
                        'id_unique': f"{data['name']}_spotify",
                        'nom': data['name'],
                        'source': 'Spotify',
                        'followers': data['followers']['total'],
                        'popularity': data['popularity'],
                        'genre': ', '.join(data['genres'][:3]) if data['genres'] else 'Non spécifié',
                        'image_url': data['images'][0]['url'] if data['images'] else '',
                        'url_spotify': data['external_urls']['spotify'],
                        'date_collecte': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    print(f" Retry OK: {data['name']}")
            else:
                print(f" Erreur {response.status_code}")
                errors.append((artist_id, f"Erreur {response.status_code}"))
        
        except Exception as e:
            print(f" Exception: {e}")
            errors.append((artist_id, str(e)))
        
        # Rate limiting : attendre 0.3s entre chaque requête
        time.sleep(0.3)
    
    print(f"\n Spotify : {len(artists_data)}/{len(artist_ids)} artistes collectés")
    if errors:
        print(f"  {len(errors)} erreurs")
    
    return pd.DataFrame(artists_data)


def collecter_deezer(artist_ids):
    """Collecter données depuis Deezer API"""
    print(f"\n Collecte Deezer de {len(artist_ids)} artistes...")
    
    artists_data = []
    errors = []
    
    for idx, artist_id in enumerate(artist_ids, 1):
        print(f"  [{idx}/{len(artist_ids)}] ID: {artist_id}...", end=" ")
        
        try:
            response = requests.get(
                f'https://api.deezer.com/artist/{artist_id}',
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Vérifier si erreur dans la réponse
                if 'error' in data:
                    print(f" {data['error']['message']}")
                    errors.append((artist_id, data['error']['message']))
                    continue
                
                artists_data.append({
                    'id_unique': f"{data['name']}_deezer",
                    'nom': data['name'],
                    'source': 'Deezer',
                    'fans': data['nb_fan'],
                    'genre': 'Non spécifié',
                    'image_url': data['picture_medium'],
                    'url_deezer': data['link'],
                    'date_collecte': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                print(f" {data['name']} ({data['nb_fan']:,} fans)")
                
            else:
                print(f"Erreur {response.status_code}")
                errors.append((artist_id, f"Erreur {response.status_code}"))
        
        except Exception as e:
            print(f" Exception: {e}")
            errors.append((artist_id, str(e)))
        
        # Rate limiting : attendre 0.2s entre chaque requête
        time.sleep(0.2)
    
    print(f"\n Deezer : {len(artists_data)}/{len(artist_ids)} artistes collectés")
    if errors:
        print(f" {len(errors)} erreurs")
    
    return pd.DataFrame(artists_data)


# ==================== MAIN ====================

if __name__ == "__main__":
    
    print(" COLLECTE AUTOMATIQUE SPOTIFY/DEEZER")
    print("=" * 60)
    print(f" Configuration:")
    print(f"   - Spotify: {len(SPOTIFY_IDS)} artistes")
    print(f"   - Deezer: {len(DEEZER_IDS)} artistes")
    print(f"   - Total: {len(SPOTIFY_IDS) + len(DEEZER_IDS)} artistes")
    
    print("\n Lancement de la collecte...")

    # Collecter
    start_time = time.time()
    
    spotify_df = collecter_spotify(SPOTIFY_IDS)
    deezer_df = collecter_deezer(DEEZER_IDS)
    
    # Sauvegarder
    date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if not spotify_df.empty:
        output_spotify = f'data/spotify_artists_collected_{date_str}.csv'
        spotify_df.to_csv(output_spotify, index=False)
        print(f"\n Spotify sauvegardé : {output_spotify}")
    
    if not deezer_df.empty:
        output_deezer = f'data/deezer_artists_collected_{date_str}.csv'
        deezer_df.to_csv(output_deezer, index=False)
        print(f" Deezer sauvegardé : {output_deezer}")
    
    # Statistiques
    elapsed = time.time() - start_time
    total = len(spotify_df) + len(deezer_df)
    
    
    print(f"Total : {total} artistes collectés")
    print(f"   - Spotify : {len(spotify_df)}/{len(SPOTIFY_IDS)} ({len(spotify_df)/len(SPOTIFY_IDS)*100:.1f}%)")
    print(f"   - Deezer : {len(deezer_df)}/{len(DEEZER_IDS)} ({len(deezer_df)/len(DEEZER_IDS)*100:.1f}%)")
    print("=" * 60)
    
    print("\nPROCHAINES ÉTAPES :")
    print("1. python filtrer_csv_emergents.py")
    print("2. python import_data.py")
    print("3. python ml_prediction.py")
    print("4. python generer_alertes.py")
    print("5. streamlit run app/streamlit.py")