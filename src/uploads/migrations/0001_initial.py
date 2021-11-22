# Generated by Django 2.2.14 on 2020-08-14 18:19

from django.db import migrations, models
import django.db.models.deletion
import uploads.models
import uploads.validators
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('identifier', models.CharField(blank=True, max_length=1024, null=True)),
                ('title', models.CharField(max_length=1024)),
                ('ereserves_record_url', models.URLField(blank=True, help_text='Libguides E-Reserves system record', max_length=1024, null=True)),
                ('barcode', models.CharField(blank=True, max_length=512, null=True, validators=[uploads.validators.validate_barcode])),
                ('form', models.CharField(choices=[('digitized', 'Digitized'), ('born_digital', 'Born Digital')], default='digitized', max_length=16)),
                ('notes', models.TextField(blank=True, null=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('size', models.IntegerField(blank=True, null=True)),
                ('published', models.BooleanField(default=False)),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_uploads.upload_set+', to='contenttypes.ContentType')),
            ],
            options={
                'base_manager_name': 'objects',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Audio',
            fields=[
                ('upload_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='uploads.Upload')),
                ('upload', models.FileField(help_text='mp3 format only', max_length=1024, upload_to='av/audio/', validators=[uploads.validators.validate_audio])),
            ],
            options={
                'base_manager_name': 'objects',
                'abstract': False,
            },
            bases=('uploads.upload',),
        ),
        migrations.CreateModel(
            name='AudioAlbum',
            fields=[
                ('upload_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='uploads.Upload')),
                ('album_directory', models.CharField(blank=True, max_length=512, null=True)),
            ],
            options={
                'base_manager_name': 'objects',
                'abstract': False,
            },
            bases=('uploads.upload',),
        ),
        migrations.CreateModel(
            name='Text',
            fields=[
                ('upload_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='uploads.Upload')),
                ('upload', models.FileField(help_text='pdf format only', max_length=1024, upload_to=uploads.models.text_upload_path, validators=[uploads.validators.validate_text])),
                ('text_type', models.CharField(choices=[('article', 'Article'), ('book_excerpt', 'Book (excerpt)'), ('book_whole', 'Book (whole)'), ('other', 'Other')], default='article', help_text='Text type cannot be changed after saving.', max_length=16)),
            ],
            options={
                'base_manager_name': 'objects',
                'abstract': False,
            },
            bases=('uploads.upload',),
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('upload_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='uploads.Upload')),
                ('upload', models.FileField(help_text='mp4 format only', max_length=1024, upload_to='av/video/', validators=[uploads.validators.validate_video])),
            ],
            options={
                'base_manager_name': 'objects',
                'abstract': False,
            },
            bases=('uploads.upload',),
        ),
        migrations.CreateModel(
            name='VideoVttTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upload', models.FileField(help_text='vtt format only', max_length=1024, upload_to='text/vtt/')),
                ('type', models.CharField(choices=[('captions', 'Captions (for hearing impairment)'), ('subtitles', 'Subtitles (for language translations)'), ('descriptions', 'Descriptions (for vision impairment)')], max_length=16)),
                ('language', models.CharField(choices=[('ab', 'Abkhazian'), ('aa', 'Afar'), ('af', 'Afrikaans'), ('ak', 'Akan'), ('sq', 'Albanian'), ('am', 'Amharic'), ('ar', 'Arabic'), ('an', 'Aragonese'), ('hy', 'Armenian'), ('as', 'Assamese'), ('av', 'Avaric'), ('ae', 'Avestan'), ('ay', 'Aymara'), ('az', 'Azerbaijani'), ('bm', 'Bambara'), ('ba', 'Bashkir'), ('eu', 'Basque'), ('be', 'Belarusian'), ('bn', 'Bengali'), ('bh', 'Bihari languages'), ('bi', 'Bislama'), ('bs', 'Bosnian'), ('br', 'Breton'), ('bg', 'Bulgarian'), ('my', 'Burmese'), ('ca', 'Catalan, Valencian'), ('ch', 'Chamorro'), ('ce', 'Chechen'), ('ny', 'Chichewa, Chewa, Nyanja'), ('zh', 'Chinese'), ('cv', 'Chuvash'), ('kw', 'Cornish'), ('co', 'Corsican'), ('cr', 'Cree'), ('hr', 'Croatian'), ('cs', 'Czech'), ('da', 'Danish'), ('dv', 'Divehi, Dhivehi, Maldivian'), ('nl', 'Dutch, Flemish'), ('dz', 'Dzongkha'), ('en', 'English'), ('eo', 'Esperanto'), ('et', 'Estonian'), ('ee', 'Ewe'), ('fo', 'Faroese'), ('fj', 'Fijian'), ('fi', 'Finnish'), ('fr', 'French'), ('ff', 'Fulah'), ('gl', 'Galician'), ('ka', 'Georgian'), ('de', 'German'), ('el', 'Greek, Modern (1453–)'), ('gn', 'Guarani'), ('gu', 'Gujarati'), ('ht', 'Haitian, Haitian Creole'), ('ha', 'Hausa'), ('he', 'Hebrew'), ('hz', 'Herero'), ('hi', 'Hindi'), ('ho', 'Hiri Motu'), ('hu', 'Hungarian'), ('ia', 'Interlingua'), ('id', 'Indonesian'), ('ie', 'Interlingue, Occidental'), ('ga', 'Irish'), ('ig', 'Igbo'), ('ik', 'Inupiaq'), ('io', 'Ido'), ('is', 'Icelandic'), ('it', 'Italian'), ('iu', 'Inuktitut'), ('ja', 'Japanese'), ('jv', 'Javanese'), ('kl', 'Kalaallisut, Greenlandic'), ('kn', 'Kannada'), ('kr', 'Kanuri'), ('ks', 'Kashmiri'), ('kk', 'Kazakh'), ('km', 'Central Khmer'), ('ki', 'Kikuyu, Gikuyu'), ('rw', 'Kinyarwanda'), ('ky', 'Kirghiz, Kyrgyz'), ('kv', 'Komi'), ('kg', 'Kongo'), ('ko', 'Korean'), ('ku', 'Kurdish'), ('kj', 'Kuanyama, Kwanyama'), ('la', 'Latin'), ('lb', 'Luxembourgish, Letzeburgesch'), ('lg', 'Ganda'), ('li', 'Limburgan, Limburger, Limburgish'), ('ln', 'Lingala'), ('lo', 'Lao'), ('lt', 'Lithuanian'), ('lu', 'Luba-Katanga'), ('lv', 'Latvian'), ('gv', 'Manx'), ('mk', 'Macedonian'), ('mg', 'Malagasy'), ('ms', 'Malay'), ('ml', 'Malayalam'), ('mt', 'Maltese'), ('mi', 'Maori'), ('mr', 'Marathi'), ('mh', 'Marshallese'), ('mn', 'Mongolian'), ('na', 'Nauru'), ('nv', 'Navajo, Navaho'), ('nd', 'North Ndebele'), ('ne', 'Nepali'), ('ng', 'Ndonga'), ('nb', 'Norwegian Bokmål'), ('nn', 'Norwegian Nynorsk'), ('no', 'Norwegian'), ('ii', 'Sichuan Yi, Nuosu'), ('nr', 'South Ndebele'), ('oc', 'Occitan'), ('oj', 'Ojibwa'), ('cu', 'Church Slavic'), ('om', 'Oromo'), ('or', 'Oriya'), ('os', 'Ossetian, Ossetic'), ('pa', 'Punjabi, Panjabi'), ('pi', 'Pali'), ('fa', 'Persian'), ('pl', 'Polish'), ('ps', 'Pashto, Pushto'), ('pt', 'Portuguese'), ('qu', 'Quechua'), ('rm', 'Romansh'), ('rn', 'Rundi'), ('ro', 'Romanian, Moldavian, Moldovan'), ('ru', 'Russian'), ('sa', 'Sanskrit'), ('sc', 'Sardinian'), ('sd', 'Sindhi'), ('se', 'Northern Sami'), ('sm', 'Samoan'), ('sg', 'Sango'), ('sr', 'Serbian'), ('gd', 'Gaelic, Scottish Gaelic'), ('sn', 'Shona'), ('si', 'Sinhala, Sinhalese'), ('sk', 'Slovak'), ('sl', 'Slovenian'), ('so', 'Somali'), ('st', 'Southern Sotho'), ('es', 'Spanish, Castilian'), ('su', 'Sundanese'), ('sw', 'Swahili'), ('ss', 'Swati'), ('sv', 'Swedish'), ('ta', 'Tamil'), ('te', 'Telugu'), ('tg', 'Tajik'), ('th', 'Thai'), ('ti', 'Tigrinya'), ('bo', 'Tibetan'), ('tk', 'Turkmen'), ('tl', 'Tagalog'), ('tn', 'Tswana'), ('to', 'Tonga (Tonga Islands)'), ('tr', 'Turkish'), ('ts', 'Tsonga'), ('tt', 'Tatar'), ('tw', 'Twi'), ('ty', 'Tahitian'), ('ug', 'Uighur, Uyghur'), ('uk', 'Ukrainian'), ('ur', 'Urdu'), ('uz', 'Uzbek'), ('ve', 'Venda'), ('vi', 'Vietnamese'), ('vo', 'Volapük'), ('wa', 'Walloon'), ('cy', 'Welsh'), ('wo', 'Wolof'), ('fy', 'Western Frisian'), ('xh', 'Xhosa'), ('yi', 'Yiddish'), ('yo', 'Yoruba'), ('za', 'Zhuang, Chuang'), ('zu', 'Zulu'), ('xx', 'Other')], default='en', max_length=2)),
                ('label', models.CharField(blank=True, help_text="Optional - Users see this. Overrides the name in the user interface generated from the Type and Language fields. Don't use this unless you know what you are doing.", max_length=16, null=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('vtt_order', models.PositiveIntegerField(db_index=True, default=0, editable=False)),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uploads.Video')),
            ],
            options={
                'ordering': ['vtt_order'],
            },
        ),
        migrations.CreateModel(
            name='AudioTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upload', models.FileField(help_text='mp3 format only', max_length=1024, upload_to='av/audio/', validators=[uploads.validators.validate_audio])),
                ('title', models.CharField(max_length=512)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('track_order', models.PositiveIntegerField(db_index=True, default=0, editable=False)),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uploads.AudioAlbum')),
            ],
            options={
                'ordering': ['track_order'],
            },
        ),
    ]
