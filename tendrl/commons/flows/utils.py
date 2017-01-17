from tendrl.commons.persistence.job_status import JobStatus


def to_camel_case(snake_str):
    return "".join(x.title() for x in snake_str.split('_'))


def update_job_status(req_id, msg, log_dict, log_level, etcd_orm):
    log_dict['all'].append(msg)
    log_dict[log_level].append(msg)
    etcd_orm.save(
        JobStatus(req_id=req_id,
                  log_info=log_dict['info'],
                  log_all=log_dict['all'],
                  log_error=log_dict['error'],
                  log_debug=log_dict['debug'],
                  log_warn=log_dict['warn']))
