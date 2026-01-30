from django.db.models import TextChoices

EMAIL_WHITELIST = [
    'lukusstricker@gmail.com',
    'michael.english3636@gmail.com',
    'joelkrznaric@gmail.com',
    'jacktecca@gmail.com',
    'ursettia1@gmail.com',
    'ibradaran@gmail.com',
    'samtalley321@gmail.com',
    'christopher.campbell1119@gmail.com',
    'gbirindelli20@gmail.com',
    'ngill0320@gmail.com',
    'dudekm1411@gmail.com',
    'georuddy@gmail.com',
    'rikomartinez39@gmail.com',
    'uhallc@gmail.com',
    'bry.biggs15@gmail.com',
    'brockwilson1@gmail.com',
    'ryancevans24@gmail.com',
]

EMAIL_TO_NAME_LOOKUP = {
    'lukusstricker@gmail.com': 'Lukus',
    'michael.english3636@gmail.com': 'Mike',
    'joelkrznaric@gmail.com': 'Joel',
    'jacktecca@gmail.com': 'Tecca',
    'ursettia1@gmail.com': 'Ursetti',
    'ibradaran@gmail.com': 'Iden',
    'samtalley321@gmail.com': 'Sam',
    'christopher.campbell1119@gmail.com': 'Chris',
    'gbirindelli20@gmail.com': 'Grant',
    'ngill0320@gmail.com': 'Nate',
    'dudekm1411@gmail.com': 'Chuck',
    'georuddy@gmail.com': 'Buster',
    'rikomartinez39@gmail.com': 'Dick',
    'uhallc@gmail.com': 'Uhall',
    'bry.biggs15@gmail.com': 'Brian',
    'brockwilson1@gmail.com': 'Brock',
    'ryancevans24@gmail.com': 'Ryan',
}

NAME_TO_EMAIL_LOOKUP = {value: key for key, value in EMAIL_TO_NAME_LOOKUP.items()}
