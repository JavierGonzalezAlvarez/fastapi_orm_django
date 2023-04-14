from django.contrib.postgres.fields import ArrayField
from django.db import models
from db.bases import ClassModel
from manage import init_django
init_django()

def empty_list():
    '''empty list for countries'''
    return []

class Users(ClassModel):
    '''model for users'''
    id = models.AutoField(primary_key=True)
    username = models.CharField(
        max_length=15,
        unique=False,
        blank=True,
        verbose_name="user Name"
    )
    useremail = models.EmailField(max_length=254, unique=True, blank=True)

    countries = ArrayField(models.CharField(max_length=2), default=empty_list)

    def save(self):
        '''save a record'''
        self.username = self.username.upper()
        super(Users, self).save()

    class Meta:
        '''meta data options'''
        db_table = "users"