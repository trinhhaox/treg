
export default {
async loadAdmin(){ this.confirmAdmUser=null; this.confirmAdmOrg=null; this.adminBusy=true;
      try{
        const [stats, orgs, users] = await Promise.all([
          this.api('/admin/stats').catch(e => { this.err = 'Lỗi thống kê: ' + (e.detail || e.status); return null; }),
          this.api('/admin/orgs').catch(e => { this.err = 'Lỗi nạp tổ chức: ' + (e.detail || e.status); return []; }),
          this.api('/admin/users').catch(e => { this.err = 'Lỗi nạp người dùng: ' + (e.detail || e.status); return []; }),
        ]);
        if(stats) this.adminStats=stats;
        if(orgs) this.adminOrgs=orgs;
        if(users) this.adminUsers=users;
      }catch(e){ this.err='Admin: '+(e.detail||e.status); }
      finally{ this.adminBusy=false; }
      this.loadAdminHub(); },
// Hub listing review: a maker's `treg hub list` is a request; approve puts the tool in search,
// reject takes it out with a reason the maker reads. A server without the hub (/meta.hub false)
// has no queue to read, so the section stays hidden without asking.
async loadAdminHub(state){ if(state) this.admHub={...this.admHub, state};
      if(!this.meta.hub){ this.admHub={...this.admHub, on:false, rows:[]}; return; }
      try{ const rows=await this.api('/admin/hub/listings?state='+this.admHub.state);
           const updates=await this.api('/admin/hub/updates').catch(()=>[]);
           this.admHub={...this.admHub, on:true, rows, updates}; }
      catch(e){ this.admHub={...this.admHub, on:false, rows:[]}; } },
async admHubUpdate(u, decision){ const reason=(this.admHub.reason['u:'+u.tool_id]||'').trim();
      if(decision==='reject' && !reason){ this.err='Write the reason first: the maker reads it.'; return; }
      this.admHub={...this.admHub, busy:u.tool_id}; this.err='';
      try{ await this.api('/admin/hub/updates/'+encodeURIComponent(u.tool_id), {method:'POST', headers:{'content-type':'application/json'}, body:JSON.stringify({decision, reason})}); }
      catch(e){ this.err='Update decision failed: '+(e.detail&&e.detail.rule||e.detail||e.status); }
      this.admHub={...this.admHub, busy:null}; await this.loadAdminHub(); },
async admHubDecide(r, decision){ const reason=(this.admHub.reason[r.tool_id]||'').trim();
      if(decision==='reject' && !reason){ this.err='Write the reason first: the maker reads it.'; return; }
      this.admHub={...this.admHub, busy:r.tool_id}; this.err='';
      // The job: what the admin typed, else the manifest's proposal (an empty box sends nothing).
      const cap=(this.admHub.cap[r.tool_id]||'').trim();
      const body={decision, reason, ...(decision==='approve' && cap ? {capability: cap==='none' ? '' : cap} : {})};
      try{ await this.api('/admin/hub/listings/'+encodeURIComponent(r.tool_id), {method:'POST', headers:{'content-type':'application/json'}, body:JSON.stringify(body)}); }
      catch(e){ this.err='Listing decision failed: '+(e.detail&&e.detail.rule||e.detail||e.status); }
      this.admHub={...this.admHub, busy:null}; await this.loadAdminHub(); },
async _adm(path, method, body){ this.adminBusy=true; this.err='';
      try{ await this.api(path, {method, ...(body?{headers:{'content-type':'application/json'},body:JSON.stringify(body)}:{})}); await this.loadAdmin(); }
      catch(e){ this.err='Admin action failed: '+(e.detail||e.status); } finally{ this.adminBusy=false; } },
admGrant(u){ this._adm('/admin/users/'+u.id+'/superadmin','POST',{value:!u.is_superadmin}); },
admSuspendUser(u){ this._adm('/admin/users/'+u.id+'/suspend','POST',{value:!u.suspended}); },
admDeleteUser(u){ if(this.confirmAdmUser!==u.id){ this.confirmAdmUser=u.id; return; } this.confirmAdmUser=null; this._adm('/admin/users/'+u.id,'DELETE'); },
admSuspendOrg(o){ this._adm('/admin/orgs/'+o.id+'/suspend','POST',{value:!o.suspended}); },
admDeleteOrg(o){ if(this.confirmAdmOrg!==o.id){ this.confirmAdmOrg=o.id; return; } this.confirmAdmOrg=null; this._adm('/admin/orgs/'+o.id,'DELETE'); },
admOpenReset(u){ this.adminResetUser=u; this.adminResetPassword=''; this.err=''; },
admCloseReset(){ this.adminResetUser=null; this.adminResetPassword=''; },
async admSubmitReset(){
  if(!this.adminResetUser) return;
  const p=(this.adminResetPassword||'').trim();
  if(!p || p.length < 6){ this.err='Mật khẩu phải có tối thiểu 6 ký tự.'; return; }
  const uid=this.adminResetUser.id;
  await this._adm('/admin/users/'+uid+'/password','POST',{password:p});
  this.admCloseReset();
},
admOpenCredit(o){
  this.adminCreditOrg = o;
  this.adminCreditAmount = '10';
  this.adminCreditReason = 'Nạp tiền thủ công từ SuperAdmin';
  this.adminCreditRef = 'adm-topup-' + o.id + '-' + Date.now();
  this.adminCreditSuccess = '';
  this.err = '';
},
admCloseCredit(){
  this.adminCreditOrg = null;
  this.adminCreditAmount = '10';
  this.adminCreditReason = '';
  this.adminCreditRef = '';
  this.adminCreditSuccess = '';
},
async admSubmitCredit(){
  if(!this.adminCreditOrg) return;
  const amt = parseFloat(this.adminCreditAmount);
  if(isNaN(amt) || amt <= 0){
    this.err = 'Vui lòng nhập số tiền hợp lệ lớn hơn 0.';
    return;
  }
  const ref = (this.adminCreditRef || '').trim() || ('adm-topup-' + this.adminCreditOrg.id + '-' + Date.now());
  const reason = (this.adminCreditReason || '').trim() || 'Nạp tiền thủ công từ SuperAdmin';
  this.adminBusy = true;
  this.err = '';
  this.adminCreditSuccess = '';
  try{
    const res = await this.api('/admin/orgs/' + this.adminCreditOrg.id + '/credit', {
      method: 'POST',
      headers: {'content-type': 'application/json'},
      body: JSON.stringify({ amount_usd: amt, ref, reason })
    });
    const newBal = (res.balance_usd != null) ? ('$' + Number(res.balance_usd).toFixed(2)) : this.money(res.balance_micro);
    this.adminCreditSuccess = 'Đã nạp thành công $' + amt.toFixed(2) + ' cho tổ chức ' + this.adminCreditOrg.name + ' (Số dư mới: ' + newBal + ')';
    if(this.adminOrgs){
      const target = this.adminOrgs.find(x => x.id === this.adminCreditOrg.id);
      if(target && res.balance_micro != null) target.balance_micro = res.balance_micro;
    }
    if(this.billing && this.activeOrgId === this.adminCreditOrg.id && res.balance_micro != null){
      this.billing.balance_micro = res.balance_micro;
    }
    setTimeout(() => {
      if(this.adminCreditSuccess){
        this.admCloseCredit();
        this.loadAdmin();
      }
    }, 1500);
  }catch(e){
    this.err = 'Lỗi nạp tiền: ' + (e.detail || e.status || e.message);
  }finally{
    this.adminBusy = false;
  }
}
}
