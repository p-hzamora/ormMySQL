from .interface import IFunction as IFunction

# Function Functions
from .aggregate.max import Max as Max
from .aggregate.min import Min as Min
from .aggregate.concat import Concat as Concat
from .aggregate.sum import Sum as Sum
from .aggregate.count import Count as Count
from .aggregate.avg import Avg as Avg
# from .group_concat import GroupConcat as GroupConcat
# from .std import Std as Std  # Standard deviation
# from .variance import Variance as Variance

# String Functions
# from .upper import Upper as Upper
# from .lower import Lower as Lower
# from .substring import Substring as Substring
# from .trim import Trim as Trim
# from .ltrim import LTrim as LTrim
# from .rtrim import RTrim as RTrim
# from .length import Length as Length
# from .char_length import CharLength as CharLength
# from .replace import Replace as Replace
# from .left import Left as Left
# from .right import Right as Right
# from .reverse import Reverse as Reverse
# from .locate import Locate as Locate  # Position of substring
# from .concat_ws import ConcatWs as ConcatWs  # Concat with separator
# from .format import Format as Format
# from .lpad import LPad as LPad
# from .rpad import RPad as RPad

# # Date/Time Functions
# from .now import Now as Now
# from .curdate import CurDate as CurDate
# from .curtime import CurTime as CurTime
# from .date import Date as Date
# from .time import Time as Time
# from .year import Year as Year
# from .month import Month as Month
# from .day import Day as Day
# from .hour import Hour as Hour
# from .minute import Minute as Minute
# from .second import Second as Second
# from .date_format import DateFormat as DateFormat
# from .date_add import DateAdd as DateAdd
# from .date_sub import DateSub as DateSub
# from .datediff import DateDiff as DateDiff
# from .timediff import TimeDiff as TimeDiff
# from .timestampdiff import TimestampDiff as TimestampDiff

# Mathematical Functions
from .mathematical.abs import Abs as Abs
from .mathematical.ceil import Ceil as Ceil
from .mathematical.floor import Floor as Floor
from .mathematical.round import Round as Round
from .mathematical.pow import Pow as Pow
from .mathematical.sqrt import Sqrt as Sqrt
from .mathematical.mod import Mod as Mod
from .mathematical.rand import Rand as Rand
from .mathematical.truncate import Truncate as Truncate

# # Conditional Functions
# from .if_ import If as If
# from .ifnull import IfNull as IfNull
# from .nullif import NullIf as NullIf
# from .coalesce import Coalesce as Coalesce
# from .case import Case as Case

# # Type Conversion Functions
# from .cast import Cast as Cast
# from .convert import Convert as Convert

# # Logical Functions
# from .greatest import Greatest as Greatest
# from .least import Least as Least

# # JSON Functions (MySQL 5.7+)
# from .json_extract import JsonExtract as JsonExtract
# from .json_object import JsonObject as JsonObject
# from .json_array import JsonArray as JsonArray

# # Other Useful Functions
# from .distinct import Distinct as Distinct
# from .md5 import MD5 as MD5
# from .sha1 import SHA1 as SHA1
# from .uuid import UUID as UUID
