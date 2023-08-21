from job import JobData

with JobData(r"C:\Users\iangs\repos\bls\test-res\TEST2") as jd:
    jd.data["date"] = "10"
