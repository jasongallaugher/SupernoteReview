import pytest
from sn.device import SupernoteDevice

def test_device_init(mock_adb_client):
    dev = SupernoteDevice()
    assert dev.device.serial == "192.168.1.5:5555"

def test_push_file(mock_adb_client, mock_device_instance):
    dev = SupernoteDevice()
    local = "local.pdf"
    remote = "/storage/emulated/0/remote.pdf"
    
    dev.push(local, remote)
    
    # Check mkdir called
    mock_device_instance.shell.assert_any_call("mkdir -p /storage/emulated/0")
    # Check push called
    mock_device_instance.sync.push.assert_called_with(local, remote)

def test_open_pdf(mock_adb_client, mock_device_instance):
    dev = SupernoteDevice()
    remote = "/storage/emulated/0/Document/test.pdf"
    
    dev.open_pdf(remote)
    
    # Verify the intent command uses /sdcard/ and specific component
    expected_cmd = (
        "am start -a android.intent.action.VIEW "
        "-d \"file:///sdcard/Document/test.pdf\" "
        "-n com.supernote.document/.MainActivity"
    )
    mock_device_instance.shell.assert_called_with(expected_cmd)

def test_list_dir(mock_adb_client, mock_device_instance):
    dev = SupernoteDevice()
    mock_device_instance.shell.return_value = "file1.pdf\nfile2.pdf\n"
    
    files = dev.list_dir("/some/dir")
    assert files == ["file1.pdf", "file2.pdf"]
    mock_device_instance.shell.assert_called_with("ls /some/dir")

def test_wireless_preference(mocker):
    # Setup mock with two devices: one USB, one Wireless
    mock_client = mocker.Mock()
    dev_usb = mocker.Mock()
    dev_usb.serial = "USB12345"
    dev_wifi = mocker.Mock()
    dev_wifi.serial = "192.168.1.10:5555"
    
    mock_client.device_list.return_value = [dev_usb, dev_wifi]
    
    mocker.patch("adbutils.AdbClient", return_value=mock_client)
    
    dev = SupernoteDevice()
    # Should pick the wifi one
    assert dev.device.serial == "192.168.1.10:5555"