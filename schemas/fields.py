from pydantic import conint, constr


TitleType = constr(min_length=1, max_length=70)
IdType = conint(ge=1)
HostType = constr(min_length=1, max_length=255)
PasswordType = constr(min_length=1, max_length=255)
UsernameType = constr(min_length=1, max_length=32)
PortType = conint(ge=1, le=65535)
