# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models


class Migration(DataMigration):

    def forwards(self, orm):
        """
        This migration populates the "verification deadline" model with
        the "expiration datetime" from the course modes table for verified
        courses.

        In the past, the course modes expiration (really an upgrade deadline)
        and the verification deadline were always set to the same value.
        With this change, the verification deadline will now be tracked in a separate
        model owned by the verify_student app.
        """

        # Retrieve all verified course modes (whether they have expired or not)
        # Unfortunately, we don't have access to constants from the application here,
        # so we hard-code the names of the course modes that require verification.
        verified_modes = orm['course_modes.CourseMode'].objects.filter(
            mode_slug__in=["verified", "professional"],
            expiration_datetime__isnull=False,
        )

        for mode in verified_modes:
            orm.VerificationDeadline.objects.create(
                course_key=mode.course_id,
                deadline=mode.expiration_datetime,
            )

    def backwards(self, orm):
        """
        Backwards migration deletes all verification deadlines.
        """
        orm.VerificationDeadline.objects.all().delete()

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'course_modes.coursemode': {
            'Meta': {'unique_together': "(('course_id', 'mode_slug', 'currency'),)", 'object_name': 'CourseMode'},
            'course_id': ('xmodule_django.models.CourseKeyField', [], {'max_length': '255', 'db_index': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'usd'", 'max_length': '8'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'expiration_date': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'expiration_datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'min_price': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'mode_display_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'mode_slug': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sku': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'suggested_prices': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'course_modes.coursemodesarchive': {
            'Meta': {'object_name': 'CourseModesArchive'},
            'course_id': ('xmodule_django.models.CourseKeyField', [], {'max_length': '255', 'db_index': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'usd'", 'max_length': '8'}),
            'expiration_date': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'expiration_datetime': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'min_price': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'mode_display_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'mode_slug': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'suggested_prices': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'verify_student.historicalverificationdeadline': {
            'Meta': {'ordering': "(u'-history_date', u'-history_id')", 'object_name': 'HistoricalVerificationDeadline'},
            'course_key': ('xmodule_django.models.CourseKeyField', [], {'max_length': '255', 'db_index': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {}),
            u'history_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'history_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'})
        },
        'verify_student.incoursereverificationconfiguration': {
            'Meta': {'ordering': "('-change_date',)", 'object_name': 'InCourseReverificationConfiguration'},
            'change_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.PROTECT'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'verify_student.skippedreverification': {
            'Meta': {'unique_together': "(('user', 'course_id'),)", 'object_name': 'SkippedReverification'},
            'checkpoint': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'skipped_checkpoint'", 'to': "orm['verify_student.VerificationCheckpoint']"}),
            'course_id': ('xmodule_django.models.CourseKeyField', [], {'max_length': '255', 'db_index': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'verify_student.softwaresecurephotoverification': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'SoftwareSecurePhotoVerification'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'error_code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'error_msg': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'face_image_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'photo_id_image_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'photo_id_key': ('django.db.models.fields.TextField', [], {'max_length': '1024'}),
            'receipt_id': ('django.db.models.fields.CharField', [], {'default': "'6644e0c2-da9b-49a4-9d0c-c19c596c911e'", 'max_length': '255', 'db_index': 'True'}),
            'reviewing_service': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'reviewing_user': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'photo_verifications_reviewed'", 'null': 'True', 'to': "orm['auth.User']"}),
            'status': ('model_utils.fields.StatusField', [], {'default': "'created'", 'max_length': '100', u'no_check_for_status': 'True'}),
            'status_changed': ('model_utils.fields.MonitorField', [], {'default': 'datetime.datetime.now', u'monitor': "u'status'"}),
            'submitted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'verify_student.verificationcheckpoint': {
            'Meta': {'unique_together': "(('course_id', 'checkpoint_location'),)", 'object_name': 'VerificationCheckpoint'},
            'checkpoint_location': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'course_id': ('xmodule_django.models.CourseKeyField', [], {'max_length': '255', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'photo_verification': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['verify_student.SoftwareSecurePhotoVerification']", 'symmetrical': 'False'})
        },
        'verify_student.verificationdeadline': {
            'Meta': {'object_name': 'VerificationDeadline'},
            'course_key': ('xmodule_django.models.CourseKeyField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'})
        },
        'verify_student.verificationstatus': {
            'Meta': {'object_name': 'VerificationStatus'},
            'checkpoint': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'checkpoint_status'", 'to': "orm['verify_student.VerificationCheckpoint']"}),
            'error': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'response': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['course_modes', 'verify_student']
    symmetrical = True
