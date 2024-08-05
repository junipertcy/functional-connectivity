import functional_connectivity as fc


def test_download_000041():
    dandi_set = fc.DandiHandler("000041", "sub-BWRat17/sub-BWRat17_ses-BWRat17-121912_ecephys.nwb")
    assert dandi_set.get_s3_url(), "https://dandiarchive.s3.amazonaws.com/blobs/ad8/b1e/ad8b1e79-102a-4cc9-98a1-1ee60d1a3396"

    dandi_set.download()
    data_array = dandi_set.get_spike_counts(100)

    assert data_array.data.shape == (29, 110), "The shape of the data array is not correct."
    