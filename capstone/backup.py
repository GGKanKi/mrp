import bcrypt


bcrypt_backup_pass = [
    bcrypt.hashpw(b"justinejade", bcrypt.gensalt()),  
    bcrypt.hashpw(b"gandanijade", bcrypt.gensalt()),
    bcrypt.hashpw(b"cutiejade", bcrypt.gensalt()),
    bcrypt.hashpw(b"capynijade", bcrypt.gensalt())
]

