#Xiaoyu API Document

## User management

### Registration 

Step 1: Get verification code

- POST: `/api/get_vcode`
- Data:
    `phonenum` - Phone number

Step 2: Register

- POST: `/api/register`
- Data:
    `phonenum` - Phone number
    `password` - **MD5 hash** of password
    `captcha` - Verification code
- On success:
    `data.uid` - User id
- On failure:
    `data.message` - Error message

### Log in

- POST: `/api/login`
- Data:
    `phonenum` - Phone number
    `password` - **MD5 hash** of password
- On success:
    `data.uid` - User id
- On failure:
    `data.message` - Error message
