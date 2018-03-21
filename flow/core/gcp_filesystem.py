__author__ = 'Bohdan Mushkevych'

from os import path

from google.cloud import storage
from google.auth import compute_engine
from google.cloud.storage import Bucket, Blob
from flow.core.abstract_filesystem import AbstractFilesystem


class GcpFilesystem(AbstractFilesystem):
    """ implementation of Google Cloud Platform Filesystem """
    def __init__(self, logger, context, **kwargs):
        super(GcpFilesystem, self).__init__(logger, context, **kwargs)
        try:
            service_account_file = self.context.settings.get('gcp_service_account_file')
            if service_account_file:
                # Explicitly use service account credentials by specifying the private key file.
                self.gcp_client = storage.Client.from_service_account_json(service_account_file)
            else:
                # Explicitly use Compute Engine credentials. These credentials are
                # available on Compute Engine, App Engine Flexible, and Container Engine.
                credentials = compute_engine.Credentials()
                self.gcp_client = storage.Client(project=context.settings['gcp_project_name'], credentials=credentials)
        except EnvironmentError as e:
            self.logger.error('Google Cloud Credentials are NOT valid. Terminating.', exc_info=True)
            raise ValueError(e)

    def __del__(self):
        pass

    def _gcp_bucket(self, bucket_name):
        if not bucket_name:
            bucket_name = self.context.settings['gcp_bucket']
        gcp_bucket = self.gcp_client.get_bucket(bucket_name)
        return gcp_bucket

    def mkdir(self, uri_path, bucket_name=None, **kwargs):
        gcp_bucket = self._gcp_bucket(bucket_name)
        folder_file = '{0}_$folder$'.format(path.basename(uri_path))
        folder_key = path.join(uri_path, folder_file)
        blob = Blob(folder_key, gcp_bucket)
        if not blob.exists():
            blob.upload_from_string(data='')

    def rmdir(self, uri_path, bucket_name=None, **kwargs):
        gcp_bucket = self._gcp_bucket(bucket_name)

        for key in gcp_bucket.list_blobs(prefix='{0}/'.format(uri_path)):
            key.delete()

    def rm(self, uri_path, bucket_name=None, **kwargs):
        gcp_bucket = self._gcp_bucket(bucket_name)
        blob = Blob(uri_path, gcp_bucket)
        blob.delete()

    def cp(self, uri_source, uri_target, bucket_name_source=None, bucket_name_target=None, **kwargs):
        gcp_bucket_source = self._gcp_bucket(bucket_name_source)
        gcp_bucket_target = self._gcp_bucket(bucket_name_target)

        blob_source = Blob(uri_source, gcp_bucket_source)
        blob_target = Blob(uri_target, gcp_bucket_target)
        blob_target.rewrite(source=blob_source)

    def mv(self, uri_source, uri_target, bucket_name_source=None, bucket_name_target=None, **kwargs):
        self.cp(uri_source, uri_target, bucket_name_source, bucket_name_target, **kwargs)
        self.rm(uri_source, bucket_name_source)

    def copyToLocal(self, uri_source, uri_target, bucket_name_source=None, **kwargs):
        gcp_bucket_source = self._gcp_bucket(bucket_name_source)
        blob = Blob(uri_source, gcp_bucket_source)
        with open(uri_target, 'wb') as file_pointer:
            blob.download_to_file(file_pointer)

    def copyFromLocal(self, uri_source, uri_target, bucket_name_target=None, **kwargs):
        gcp_bucket_target = self._gcp_bucket(bucket_name_target)
        blob = Blob(uri_target, gcp_bucket_target)
        with open(uri_source, 'rb') as file_pointer:
            blob.upload_from_file(file_pointer)

    def exists(self, uri_path, bucket_name=None,  **kwargs):
        gcp_bucket = self._gcp_bucket(bucket_name)
        blob = Blob(uri_path, gcp_bucket)
        return blob.exists()