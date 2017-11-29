## priortize cron jobs
* deploy candlepin in HOSTED MODE
* pause scheduler by making REST request:

```
POST https://localhost:8443/candlepin/jobs/scheduler ( contenttype application/json, request body: "false" )

```
* make any async job request :
```
curl -X PUT  -k -u admin:admin  "https://localhost:8443/candlepin/owners/admin/subscriptions" 
```

then use following sql to verify appropriate priorities:

```
select distinct priority, trigger_group from qrtz_triggers;
select job_name , priority from qrtz_triggers;
```


## Force re-trigger cron jobs

* deploy candlepin

```
deploy -gat
```
* show canceljobjob is running in logs
* block all jobs and show cancel job is stopped in logs
```
update qrtz_triggers set trigger_state = 'BLOCKED';
```
* retrigger CancelJobJob and show in logs its running again.

```
POST https://localhost:8443/candlepin/jobs/retrigger/CancelJobJob

```
* show the newly created trigger

```
select * from qrtz_trigger

```

* only legit cron jobs can be retriggered using this API, so these wont work

```
POST https://localhost:8443/candlepin/jobs/retrigger/DoesNotExistJob
POST https://localhost:8443/candlepin/jobs/retrigger/HypervisorCheckinJob

```
* the job name is case insensitive, so this will work:

```
POST https://localhost:8443/candlepin/jobs/retrigger/canceljobJob

```

* NOTE: this will only retrigger the job, not run it. for example,
* lets set all pools to expire:

```
select count(*) from cp_pool;
update cp_pool set enddate = (select date 'yesterday');

```
* now retriggerring the job does not help immediately, cause it will run at midnight only:

```
POST https://localhost:8443/candlepin/jobs/retrigger/ExpiredPoolsJob

select count(*) from cp_pool;
```
* instead, we have a schedule API which will fire the job immediately, asynchronously.
```
POST https://localhost:8443/candlepin/jobs/schedule/ExpiredPoolsJob
select count(*) from cp_pool;
```
