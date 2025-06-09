import typing as tp
import typing_extensions as tpe

LITERAL_TYPES = frozenset([tp.Literal, tpe.Literal])

type _AnnotationScanType = tp.Type[tp.Any] | str | tp.NewType
