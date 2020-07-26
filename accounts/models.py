from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, 
    AbstractBaseUser
)

def no_accent_vietnamese(s):
    s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
    s = re.sub(r'[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
    s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
    s = re.sub(r'[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', s)
    s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
    s = re.sub(r'[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', s)
    s = re.sub(r'[ìíịỉĩ]', 'i', s)
    s = re.sub(r'[ÌÍỊỈĨ]', 'I', s)
    s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
    s = re.sub(r'[ƯỪỨỰỬỮÙÚỤỦŨ]', 'U', s)
    s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
    s = re.sub(r'[ỲÝỴỶỸ]', 'Y', s)
    s = re.sub(r'[Đ]', 'D', s)
    s = re.sub(r'[đ]', 'd', s)
    return s

class UserManager(BaseUserManager):
    def create_user(self, mobile=None, email=None, fullname=None, username=None, password=None, user_slug=None, anonymous=True, is_active=True, is_staff=False, is_admin=False, timestamp=None, timesupdate=None):
        if not email:
            raise ValueError("Trường email không được bỏ trống.")
        if not password:
            raise ValueError(_("Trường mật khẩu không được bỏ trống"))
        user_obj = self.model(
            email = self.normalize_email(email),
            fullname=fullname
        )
        user_obj.set_password(password) # thay đổi mật khẩu người dùng
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.is_active = is_active
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, email,fullname=None, password=None):
        user = self.create_user(
                email,
                fullname=fullname,
                password=password,
                is_staff=True
        )
        return user

    def create_superuser(self, email, fullname=None, password=None):
        user = self.create_user(
                email,
                fullname=fullname,
                password=password,
                is_staff=True,
                is_admin=True
        )
        return user

class User(AbstractBaseUser):
    mobile          = models.IntegerField(max_length=12, unique=True, verbose_name='Số Điện Thại')
    email           = models.EmailField( max_length=100, unique=True, verbose_name='Email')
    fullname        = models.CharField(max_length=100, verbose_name='Họ và Tên')
    username        = models.CharField(max_length=100, verbose_name='Tài Khoản')
    password        = models.CharField(max_length=100, verbose_name='Mật Khẩu')
    user_slug       = models.SlugField(null=True, blank=True, max_length=50)
    anonymous       = models.BooleanField(default=True) # Người dùng không không đăng nhập
    is_active       = models.BooleanField(default=True) # có thể đăng nhập
    staff           = models.BooleanField(default=False) # là người quản trị nhưng ko phải superuser
    admin           = models.BooleanField(default=False) # superuser
    timestamp       = models.DateTimeField(auto_now_add=True)
    timesupdate     = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username' # đăng nhập bằng email
    REQUIRED_FIELDS = ['fullname'] # .\manage.py createsuperuser

    objects = UserManager()
    
    def __str__(self):
        if self.email:
            return self.email
        elif self.mobile:
            return self.mobile

    def username(self):
        if self.email:
            return self.email
        elif self.mobile:
            return self.mobile

    def get_fullname(self):
        if self.fullname:
            return self.fullname
        return self.email

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        if self.is_admin:
            return True
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    class Meta:
        verbose_name = 'Người Dùng'
        verbose_name_plural = 'Người Dùng'

    def save(self, *args, **kwargs):
        slug_name = self.no_accent_vietnamese(self.fullname)
        self.user_slug = slugify(slug_name)
        super(User, self).save(*args, **kwargs)