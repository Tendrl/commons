import maps
from mock import patch


from tendrl.commons import objects
from tendrl.commons.objects.job import Job


def load(*args):
    parent = Job(job_id="Test Parent Job Id", status="Active",
                 payload=maps.NamedDict())
    if args[0]:
        parent.errors = "Error Message"
        parent.children = ["Test_child"]
    return parent


# Testing __init__
def test_constructor():
    '''Testing for constructor involves checking if all needed

    variables are declared initialized
    '''
    job = Job()
    assert job.job_id is None
    # Passing Dummy Values
    job = Job(job_id="Test job id", payload="Test Payload",
              status=True, errors=None, children=None,
              locked_by=None, output="Job Done")
    assert job.output == "Job Done"


# Testing save
@patch.object(objects.BaseObject, "save", return_value=None)
def test_save(mock_save):
    job = Job()
    payload = maps.NamedDict()
    payload['parent'] = "Test Parent Job Id"
    job.payload = payload
    with patch.object(objects.BaseObject, 'load') as mock_load:
        mock_load.return_value = load(False)
        job.status = "true"
        job.save()
    with patch.object(objects.BaseObject, 'load') as mock_load:
        mock_load.return_value = load(False)
        job.status = "failed"
        job.save()
    with patch.object(objects.BaseObject, 'load') as mock_load:
        mock_load.return_value = load(True)
        job.status = "failed"
        job.save()


# Testing render
def test_render():
    job = Job()
    assert job.render() is not None
