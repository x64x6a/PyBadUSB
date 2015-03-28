#include <Python.h>
#include <structmember.h>
#include <windows.h>
#include <ntddscsi.h> 

typedef unsigned char uint8_t;
#define SCSI_IOCTL_DATA_OUT               0
#define SCSI_IOCTL_DATA_IN                1
#define SCSI_IOCTL_DATA_UNSPECIFIED       2
#define SCSI_IOCTL_DATA_IO_SIZE           0x50
#define DEFAULT_TIMEOUT                   30

/*
			Internal Functions
*/
static SCSI_PASS_THROUGH_DIRECT *getSPTD(unsigned char direction, unsigned timeout, unsigned char *cdb, unsigned cdb_size, void *data, unsigned data_size)
{
	uint8_t cmd[SCSI_IOCTL_DATA_IO_SIZE];
	memset(cmd, 0, SCSI_IOCTL_DATA_IO_SIZE);

	SCSI_PASS_THROUGH_DIRECT *sptd = (SCSI_PASS_THROUGH_DIRECT *)cmd;
	sptd->Length = sizeof(SCSI_PASS_THROUGH_DIRECT);
	sptd->TimeOutValue = timeout;
	sptd->PathId = 0;
	sptd->TargetId = 1;
	sptd->Lun = 0;
	sptd->CdbLength = cdb_size;
	sptd->SenseInfoLength = 0x18;
	sptd->DataIn = direction;
	sptd->DataTransferLength = data_size;
	sptd->DataBuffer = data;
	sptd->SenseInfoOffset = 0x30;
	memcpy(sptd->Cdb, cdb, cdb_size);

	return sptd;
}

/*
			SCSI Device Object
*/
typedef struct {
	PyObject_HEAD
	PyObject *timeout;
	PyObject *handle;
} SCSI_Object;

static void
SCSI_dealloc(SCSI_Object* self)
{
	Py_XDECREF(self->handle);
	Py_XDECREF(self->timeout);
	self->ob_type->tp_free((PyObject*)self);
}

/*
			SCSI Object methods
*/
static PyObject *
SCSI_read(PyObject *self, PyObject *args)
{
	unsigned char *cdb;
	void *data;
	unsigned int cdb_size, data_size;
	int timeout, status;
	DWORD BytesReturned = 0;
	HANDLE handle;
	PyObject *response;
	SCSI_PASS_THROUGH_DIRECT *sptd;

	if (!PyArg_ParseTuple(args, "s#I", &cdb, &cdb_size, &data_size))
		return NULL;
	PyArg_Parse(((SCSI_Object *)self)->timeout, "i", &timeout);
	PyArg_Parse(((SCSI_Object *)self)->handle, "i", &handle);
	data = (void *) malloc(sizeof(char)*data_size);
	

	sptd = getSPTD(SCSI_IOCTL_DATA_IN, timeout, cdb, cdb_size, data, data_size);
	status = DeviceIoControl(handle, IOCTL_SCSI_PASS_THROUGH_DIRECT, sptd, SCSI_IOCTL_DATA_IO_SIZE, sptd, SCSI_IOCTL_DATA_IO_SIZE, &BytesReturned, 0);
	if (status)
	{
		response = Py_BuildValue("s#", data, data_size);
		free(data);
		return response;
	}
	else
	{
		// throw error according to GetLastError() and/or status ?
		free(data);
		Py_INCREF(Py_None);
		return Py_None;
	}
}

static PyObject *
SCSI_write(PyObject *self, PyObject *args)
{
	unsigned char *cdb;
	void *data;
	unsigned int cdb_size, data_size;
	int timeout, status;
	DWORD BytesReturned = 0;
	HANDLE handle;
	PyObject *response;
	SCSI_PASS_THROUGH_DIRECT *sptd;

	if (!PyArg_ParseTuple(args, "s#s#", &cdb, &cdb_size, &data, &data_size))
		return NULL;
	PyArg_Parse(((SCSI_Object *)self)->timeout, "i", &timeout);
	PyArg_Parse(((SCSI_Object *)self)->handle, "i", &handle);

	sptd = getSPTD(SCSI_IOCTL_DATA_OUT, timeout, cdb, cdb_size, data, data_size);
	status = DeviceIoControl(handle, IOCTL_SCSI_PASS_THROUGH_DIRECT, sptd, SCSI_IOCTL_DATA_IO_SIZE, sptd, SCSI_IOCTL_DATA_IO_SIZE, &BytesReturned, 0);
	
	// throw error (if(!status)) according to GetLastError() and/or status ?
	response = Py_BuildValue("i", status);
	return response;
}

static PyObject *
SCSI_close(PyObject *self)
{
	PyObject *new_handle, *tmp;
	int handle;

	if (!PyArg_Parse(((SCSI_Object *)self)->handle, "i", &handle))
	{
		Py_INCREF(Py_None);
		return Py_None;
	}
	
	if ((HANDLE)handle != INVALID_HANDLE_VALUE)
	{
		new_handle = Py_BuildValue("i", (int)INVALID_HANDLE_VALUE);
		tmp = ((SCSI_Object *)self)->handle;
		Py_INCREF(new_handle);
		((SCSI_Object *)self)->handle = new_handle;
		Py_XDECREF(tmp);
		CloseHandle(tmp);
	}
	
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
SCSI_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	SCSI_Object *self;

	self = (SCSI_Object *)type->tp_alloc(type, 0);
	if(self != NULL){
		self->timeout = Py_BuildValue("i", DEFAULT_TIMEOUT);
		if(self->timeout == NULL){
			Py_DECREF(self);
			return NULL;
		}
		
		self->handle = Py_BuildValue("i", INVALID_HANDLE_VALUE);
	}

	return (PyObject *)self;
}

static int
SCSI_init(SCSI_Object *self, PyObject *args, PyObject *kwds)
{
	int _timeout = DEFAULT_TIMEOUT,
		_handle; 
	PyObject *timeout, *handle, *tmp;
	
	static char *kwlist[] = {"handle", "timeout", NULL};
	if (! PyArg_ParseTupleAndKeywords(args, kwds, "i|i", kwlist, 
										&_handle, &_timeout))
		return -1;
	
	// handle
	handle = Py_BuildValue("i", _handle);
	tmp = self->handle;
	Py_INCREF(handle);
	self->handle = handle;
	Py_DECREF(tmp);
	
	// timeout
	if (_timeout){
		timeout = Py_BuildValue("i", _timeout);
	}
	else {
		timeout = Py_BuildValue("i", DEFAULT_TIMEOUT);
	}
	tmp = self->timeout;
	Py_INCREF(timeout);
	self->timeout = timeout;
	Py_DECREF(tmp);

	return 0;
}


/*
			SCSI Object Setup
*/
static PyMemberDef SCSI_members[] = {
	{"handle",  T_OBJECT_EX, offsetof(SCSI_Object,  handle), 0, "SCSI device handle"},
	{"timeout", T_OBJECT_EX, offsetof(SCSI_Object, timeout), 0, "timeout"},
	{NULL}  /* Sentinel */
};

static PyMethodDef SCSI_methods[] = {
	{"write",             SCSI_write, METH_VARARGS, "write(cdb, data) -> returns DeviceIoControl response integer"},
	{"read",               SCSI_read, METH_VARARGS, "read(cdb, data_size) -> returns read string of length data_size after sending cdb"},
	{"close",(PyCFunction)SCSI_close,  METH_NOARGS, "close() -> closes SCSI object handle"},
	{NULL}  /* Sentinel */
};

static PyTypeObject SCSIType = {
	PyObject_HEAD_INIT(NULL)
	0,                         /*ob_size*/
	"scsi.SCSI",               /*tp_name*/
	sizeof(SCSI_Object),       /*tp_basicsize*/
	0,                         /*tp_itemsize*/
	(destructor)SCSI_dealloc,  /*tp_dealloc*/
	0,                         /*tp_print*/
	0,                         /*tp_getattr*/
	0,                         /*tp_setattr*/
	0,                         /*tp_compare*/
	0,                         /*tp_repr*/
	0,                         /*tp_as_number*/
	0,                         /*tp_as_sequence*/
	0,                         /*tp_as_mapping*/
	0,                         /*tp_hash */
	0,                         /*tp_call*/
	0,                         /*tp_str*/
	0,                         /*tp_getattro*/
	0,                         /*tp_setattro*/
	0,                         /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,        /*tp_flags*/
	"SCSI handle object",      /* tp_doc */
	0,                         /* tp_traverse */
	0,                         /* tp_clear */
	0,                         /* tp_richcompare */
	0,                         /* tp_weaklistoffset */
	0,                         /* tp_iter */
	0,                         /* tp_iternext */
	SCSI_methods,              /* tp_methods */
	SCSI_members,              /* tp_members */
	0,                         /* tp_getset */
	0,                         /* tp_base */
	0,                         /* tp_dict */
	0,                         /* tp_descr_get */
	0,                         /* tp_descr_set */
	0,                         /* tp_dictoffset */
	(initproc)SCSI_init,       /* tp_init */
	0,                         /* tp_alloc */
	SCSI_new,                  /* tp_new */
};

/*
			Module Functions
*/
static PyObject *
scsi_open(PyObject *self, PyObject *args)
{
	char *device_name;
	HANDLE handle;
	PyObject *SCSI_args = NULL;
	PyObject *SCSI_kwds = NULL;
	SCSI_Object *device;

	if (!PyArg_ParseTuple(args, "s", &device_name))
		return NULL;
	
#if defined(UNICODE) || defined(_UNICODE)
	wchar_t *path = (wchar_t *) malloc((strlen(device_name)/sizeof(char))*sizeof(wchar_t));
	mbstowcs(path, device_name, strlen(device_name)+sizeof(char));
	handle = CreateFile(path, 
		GENERIC_READ | GENERIC_WRITE,
		FILE_SHARE_READ | FILE_SHARE_WRITE,
		0,
		OPEN_EXISTING,
		0x20000000,
		0
	);
	free(path);
#else
	handle = CreateFile(device_name, 
		GENERIC_READ | GENERIC_WRITE,
		FILE_SHARE_READ | FILE_SHARE_WRITE,
		0,
		OPEN_EXISTING,
		0x20000000,
		0
	);
#endif
	
	if (handle==INVALID_HANDLE_VALUE){
		Py_INCREF(Py_None);
		return Py_None;
	}
	
	Py_INCREF(&SCSIType);
	device = (SCSI_Object *) SCSI_new(&SCSIType, NULL, NULL);
	SCSI_args = Py_BuildValue("ii", (int) handle, DEFAULT_TIMEOUT);
	
	if(SCSI_init(device, SCSI_args, SCSI_kwds)){
		Py_INCREF(Py_None);
		return Py_None;
	}
	
	return (PyObject *)device;
}

/*
			Module Setup
*/
static PyMethodDef scsi_Methods[] = {
	{"open",  scsi_open, METH_VARARGS, "Returns SCSI device object if succeeds, otherwise returns None."},
	{NULL, NULL, 0, NULL}
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif

PyMODINIT_FUNC
initscsi(void)
{
	PyObject* m;
	if (PyType_Ready(&SCSIType) < 0)
		return;
	
	m = Py_InitModule3("scsi", scsi_Methods, "Creates SCSI a object.");
	if (m == NULL)
		return;

	Py_INCREF(&SCSIType);
	PyModule_AddObject(m, "SCSI", (PyObject *)&SCSIType);
}

int
main(int argc, char *argv[])
{
	Py_SetProgramName(argv[0]);
	Py_Initialize();
	initscsi();
}