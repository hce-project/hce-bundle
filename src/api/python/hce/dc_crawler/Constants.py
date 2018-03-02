"""
  HCE project, Python bindings, Distributed Tasks Manager application.
  Event objects definitions.

  @package: dc
  @file Constants.py
  @author Oleksii <developers.hce@gmail.com>
  @author madk <developers.hce@gmail.com>
  @link: http://hierarchical-cluster-engine.com/
  @copyright: Copyright &copy; 2013-2014 IOIX Ukraine
  @license: http://hierarchical-cluster-engine.com/license/
  @since: 0.1
  """

# limit fetcher 100 sec
FETCHER_TIME_LIMIT_MAX = 100
CONNECTION_TIMEOUT = 1.0

MAX_HTTP_REDIRECTS_LIMIT = 5
MAX_HTTP_SIZE_UNLIMIT = 0

MAX_HTML_REDIRECTS_LIMIT = 1

DB_SITES = "dc_sites"
DB_URLS = "dc_urls"

RTC_FINALIZER_APP_NAME = "rtc-finalizer"
RTC_PREPROCESSOR_APP_NAME = "rtc-preprocessor"

# List of allowed names for getting 'pubdate' from feed
pubdateFeedNames = ["pubdate", "published", "pubDate", "published_parsed", "updated_parsed"]
pubdateRssFeedHeaderName = "X-pubdateRssFeed"
rssFeedUrlHeaderName = "X-feed_url"
baseUrlHeaderName = "X-base_url"

HTTP_CODE_200 = 200
HTTP_CODE_304 = 304
HTTP_CODE_400 = 400
HTTP_CODE_403 = 403

REDIRECT_HTTP_CODES = [301, 302, 303, 304]
REDIRECT_HEADER_FIELDS_FOR_REMOVE = ['referer', 'content-type', 'Location', 'cookie']

# Dict of charsets used in class SimpleCharsetDetector for cast from wrong encoding name to correct encoding name
charsetDetectorMap = {
    'win-1251':'windows-1251',
    'UTF-8':'utf8',
    'utf-8':'utf8'
}

# # dictionary of pair Codec as key and Aliases as value string
standardEncodings = {
    'ascii':'646, us-ascii',
    'big5':'big5-tw, csbig5',
    'big5hkscs':'big5-hkscs, hkscs',
    'cp037':'IBM037, IBM039',
    'cp424':'EBCDIC-CP-HE, IBM424',
    'cp437':'437, IBM437',
    'cp500':'EBCDIC-CP-BE, EBCDIC-CP-CH, IBM500',
    'cp720':'',
    'cp737':'',
    'cp775':'IBM775',
    'cp850':'850, IBM850',
    'cp852':'852, IBM852',
    'cp855':'855, IBM855',
    'cp856':'',
    'cp857':'857, IBM857',
    'cp858':'858, IBM858',
    'cp860':'860, IBM860',
    'cp861':'861, CP-IS, IBM861',
    'cp862':'862, IBM862',
    'cp863':'863, IBM863',
    'cp864':'IBM864',
    'cp865':'865, IBM865',
    'cp866':'866, IBM866',
    'cp869':'869, CP-GR, IBM869',
    'cp874':'',
    'cp875':'',
    'cp932':'932, ms932, mskanji, ms-kanji',
    'cp949':'949, ms949, uhc',
    'cp950':'950, ms950',
    'cp1006':'',
    'cp1026':'ibm1026',
    'cp1140':'ibm1140',
    'cp1250':'windows-1250',
    'cp1251':'windows-1251',
    'cp1252':'windows-1252',
    'cp1253':'windows-1253',
    'cp1254':'windows-1254',
    'cp1255':'windows-1255',
    'cp1256':'windows-1256',
    'cp1257':'windows-1257',
    'cp1258':'windows-1258',
    'euc_jp':'eucjp, ujis, u-jis',
    'euc_jis_2004':'jisx0213, eucjis2004',
    'euc_jisx0213':'eucjisx0213',
    'euc_kr':'euckr, korean, ksc5601, ks_c-5601, ks_c-5601-1987, ksx1001, ks_x-1001',
    'gb2312':'chinese, csiso58gb231280, euc- cn, euccn, eucgb2312-cn, gb2312-1980, gb2312-80, iso- ir-58',
    'gbk':'936, cp936, ms936',
    'gb18030':'gb18030-2000',
    'hz':'hzgb, hz-gb, hz-gb-2312',
    'iso2022_jp':'csiso2022jp, iso2022jp, iso-2022-jp',
    'iso2022_jp_1':'iso2022jp-1, iso-2022-jp-1',
    'iso2022_jp_2':'iso2022jp-2, iso-2022-jp-2',
    'iso2022_jp_2004':'iso2022jp-2004, iso-2022-jp-2004',
    'iso2022_jp_3':'iso2022jp-3, iso-2022-jp-3',
    'iso2022_jp_ext':'iso2022jp-ext, iso-2022-jp-ext',
    'iso2022_kr':'csiso2022kr, iso2022kr, iso-2022-kr',
    'latin_1':'iso-8859-1, iso8859-1, 8859, cp819, latin, latin1, L1',
    'iso8859_2':'iso-8859-2, latin2, L2',
    'iso8859_3':'iso-8859-3, latin3, L3',
    'iso8859_4':'iso-8859-4, latin4, L4',
    'iso8859_5':'iso-8859-5, cyrillic',
    'iso8859_6':'iso-8859-6, arabic',
    'iso8859_7':'iso-8859-7, greek, greek8',
    'iso8859_8':'iso-8859-8, hebrew',
    'iso8859_9':'iso-8859-9, latin5, L5',
    'iso8859_10':'iso-8859-10, latin6, L6',
    'iso8859_11':'iso-8859-11, thai',
    'iso8859_13':'iso-8859-13, latin7, L7',
    'iso8859_14':'iso-8859-14, latin8, L8',
    'iso8859_15':'iso-8859-15, latin9, L9',
    'iso8859_16':'iso-8859-16, latin10, L10',
    'johab':'cp1361, ms1361',
    'koi8_r':'',
    'koi8_u':'',
    'mac_cyrillic':'maccyrillic',
    'mac_greek':'macgreek',
    'mac_iceland':'maciceland',
    'mac_latin2':'maclatin2, maccentraleurope',
    'mac_roman':'macroman',
    'mac_turkish':'macturkish',
    'ptcp154':'csptcp154, pt154, cp154, cyrillic-asian',
    'shift_jis':'csshiftjis, shiftjis, sjis, s_jis',
    'shift_jis_2004':'shiftjis2004, sjis_2004, sjis2004',
    'shift_jisx0213':'shiftjisx0213, sjisx0213, s_jisx0213',
    'utf_32':'U32, utf32',
    'utf_32_be':'UTF-32BE',
    'utf_32_le':'UTF-32LE',
    'utf_16':'U16, utf16',
    'utf_16_be':'UTF-16BE',
    'utf_16_le':'UTF-16LE',
    'utf_7':'U7, unicode-1-1-utf-7',
    'utf_8':'U8, UTF, utf8',
    'utf_8_sig':''}
