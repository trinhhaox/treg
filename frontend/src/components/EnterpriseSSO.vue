<script>
import { useDashboard } from '../state/context'

export default {
  props: { orgId: { type: Number, required: true }, slug: { type: String, required: true }, owner: Boolean },
  setup: useDashboard,
  data: () => ({ sso: null, blockedMembers: [], busy: '', error: '', message: '', itEmail: '', showInviteIT: false }),
  watch: { orgId() { this.loadSSO() } },
  mounted() { this.loadSSO() },
  computed: {
    subscribed() { return this.sso && ['active', 'trialing', 'past_due'].includes(this.sso.subscription_status) },
    directoryPlan() { return this.sso?.plan === 'sso_directory' },
    setupStepCount() { return this.directoryPlan ? 3 : 2 },
    completedSteps() {
      if (!this.sso) return 0
      return Number(this.sso.sso_ready) + Number(this.directoryPlan && this.sso.directory_ready) + Number(this.sso.enforced)
    },
  },
  methods: {
    formatUsdCents(cents) {
      return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(cents / 100)
    },
    async copyEmployeeLink() {
      const url = new URL(`/auth/sso/${encodeURIComponent(this.slug)}/start`, location.origin).href
      this.message = await this.toClipboard(url) ? 'Đã sao chép liên kết đăng nhập cho nhân viên.' : 'Không thể sao chép liên kết.'
    },
    async loadSSO() {
      this.sso = null
      this.blockedMembers = []
      try {
        this.sso = await this.api(`/orgs/${this.orgId}/sso`)
        if (this.owner) this.blockedMembers = (await this.api(`/orgs/${this.orgId}/sso/blocked`)).members
      }
      catch (e) { this.error = e.detail || 'Không thể tải cài đặt SSO.' }
    },
    async action(kind, path, body) {
      this.busy = kind; this.error = ''; this.message = ''
      try {
        const result = await this.api(`/orgs/${this.orgId}/sso/${path}`, {
          method: 'POST', headers: { 'content-type': 'application/json' },
          body: JSON.stringify(body || {}),
        })
        if (result.url) { location.href = result.url; return }
        this.message = kind === 'enforce' ? 'Đã lưu cấu hình quyền truy cập SSO.' :
          kind === 'cancel' ? 'Gói đăng ký sẽ kết thúc sau kỳ thanh toán hiện tại.' : 'Đã lưu.'
        await this.loadSSO()
      } catch (e) { this.error = e.detail || `Không thể thực hiện thao tác ${kind}.` }
      finally { this.busy = '' }
    },
    async inviteIT() {
      const email = this.itEmail.trim()
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { this.error = "Vui lòng nhập email quản trị viên IT của bạn."; return }
      await this.action('gửi lời mời quản trị IT', 'invite-it', { email })
      if (!this.error) this.message = 'WorkOS đã gửi thư mời thiết lập tới quản trị viên IT.'
    },
    async restoreMember(userId) {
      await this.action('khôi phục quyền truy cập SSO', `blocked/${userId}/restore`)
      if (!this.error) this.message = 'Nhân viên này đã có thể đăng nhập lại qua SSO.'
    },
  },
}
</script>

<template>
  <section class="sso-page" aria-label="Cài đặt đăng nhập một lần SSO">
    <header class="sso-heading">
      <div>
        <div class="lbl">TRUY CẬP ĐỘI NGŨ</div>
        <h2>Đăng nhập doanh nghiệp (SSO)</h2>
        <p v-if="owner">Cho phép nhân viên tham gia đội ngũ này thông qua nhà cung cấp danh tính (IdP) của công ty bạn. Họ tham gia với tư cách thành viên; bạn có thể thay đổi vai trò trong mục Thành viên.</p>
        <p v-else>Đội ngũ của bạn đã kết nối tính năng đăng nhập doanh nghiệp. Hãy sử dụng liên kết nhân viên để đăng nhập hoặc chia sẻ cho đồng nghiệp.</p>
      </div>
      <span v-if="owner && subscribed" class="sso-progress">Đã hoàn thành {{completedSteps}} / {{setupStepCount}} bước</span>
    </header>

    <p v-if="error" class="banner" role="alert">{{error}}</p>
    <p v-if="message" class="tut-notice" role="status">{{message}}</p>

    <template v-if="sso?.sso_ready && subscribed && !owner">
      <div class="sso-panel">
        <h3>Đăng nhập doanh nghiệp đã sẵn sàng</h3>
        <p class="sso-muted">Liên kết này khởi động quá trình đăng nhập doanh nghiệp và có thể chia sẻ cho đồng nghiệp có quyền truy cập qua nhà cung cấp danh tính của bạn.</p>
        <button class="btn sso-button" @click="copyEmployeeLink">Sao chép liên kết đăng nhập nhân viên</button>
      </div>
    </template>

    <template v-if="owner && sso">
      <div v-if="!sso.configured || !sso.billing_configured" class="sso-panel">
        <h3>Tính năng chưa khả dụng</h3>
        <p class="sso-muted">Hệ thống WorkOS và thanh toán cần được cấu hình trên máy chủ này trước khi bạn có thể thiết lập đăng nhập doanh nghiệp.</p>
      </div>

      <template v-else-if="!subscribed">
        <div class="sso-section-head"><div class="lbl">GÓI DỊCH VỤ</div><h3>Chọn phương thức truy cập cho nhân viên</h3></div>
        <div v-if="sso.enforced" class="sso-panel">
          <p class="sso-muted">Đội ngũ này vẫn đang bắt buộc dùng SSO. Hãy cho phép đăng nhập thông thường trước khi đổi gói.</p>
          <button class="btn sm sso-button" :disabled="!!busy" @click="action('enforce','enforce',{enabled:false})">Cho phép đăng nhập thông thường</button>
        </div>
        <p v-if="sso.cleanup_pending" class="sso-panel sso-muted">Cấu hình SSO trước đó đang được dọn dẹp. Bạn có thể đăng ký lại khi quá trình hoàn tất.</p>
        <div v-if="sso.plans.length" class="sso-plan-grid">
          <article v-for="plan in sso.plans" :key="plan.id" class="sso-panel sso-plan">
            <div class="sso-plan-top"><span class="sso-plan-mark" aria-hidden="true">{{plan.directory_sync?'✦':'◇'}}</span><span v-if="plan.directory_sync" class="sso-pill">Tự động đồng bộ & thu hồi</span></div>
            <h4>{{plan.directory_sync?'SSO + Đồng bộ danh bạ (Directory Sync)':'Chỉ đăng nhập SSO'}}</h4>
            <p class="sso-muted">{{plan.directory_sync?'Nhân viên đăng nhập bằng SSO. Thay đổi trong danh bạ công ty sẽ tự động thu hồi quyền truy cập và khóa của họ.':'Nhân viên đăng nhập bằng SSO. Quản trị viên đội ngũ thu hồi quyền truy cập và khóa thủ công.'}}</p>
            <div class="sso-price"><strong>{{formatUsdCents(plan.usd_monthly_cents)}}</strong><span>/ tháng, mỗi đội ngũ</span></div>
            <button class="btn sso-button" :class="plan.directory_sync?'primary':''" :disabled="!!busy || sso.cleanup_pending" @click="action('checkout','checkout',{plan:plan.id,price_id:plan.price_id})">
              Chọn {{plan.directory_sync?'SSO + Đồng bộ danh bạ':'Chỉ SSO'}} <span aria-hidden="true">→</span>
            </button>
          </article>
        </div>
        <p v-else-if="!sso.cleanup_pending" class="sso-panel sso-muted">Các gói đăng ký tạm thời chưa sẵn sàng. Vui lòng thử lại sau.</p>
      </template>

      <template v-else>
        <div class="sso-panel sso-current-plan">
          <div class="sso-plan-summary">
            <div><div class="lbl">GÓI HIỆN TẠI</div><h3>{{directoryPlan?'SSO + Đồng bộ danh bạ':'Chỉ SSO'}}</h3><p class="sso-muted">{{directoryPlan?'Đăng nhập doanh nghiệp và tự động thu hồi quyền nhân viên':'Đăng nhập doanh nghiệp; xóa nhân viên khỏi đội ngũ thủ công'}}</p></div>
            <span class="sso-pill" :class="sso.subscription_status==='past_due'?'sso-pill-warn':'sso-pill-ok'">{{sso.subscription_status==='past_due'?'Đang thử lại thanh toán':sso.cancel_at_period_end?'Hết hạn cuối kỳ':'Đang hoạt động'}}</span>
          </div>
          <p v-if="sso.subscription_status==='past_due'" class="sso-payment-note">Khoản thanh toán đang được thử lại. SSO vẫn hoạt động. Vui lòng cập nhật phương thức thanh toán trong mục Thanh toán.</p>
          <div class="sso-plan-foot">
            <span>{{sso.cancel_at_period_end?'Cấu hình của bạn vẫn khả dụng cho đến khi kỳ thanh toán kết thúc.':'Hóa đơn gói SSO tách biệt với số dư nạp trước cho công cụ.'}}</span>
            <button v-if="!sso.cancel_at_period_end" class="sso-text-action" :disabled="!!busy" @click="action('cancel','cancel')">Hủy gói vào cuối chu kỳ thanh toán</button>
          </div>
        </div>

        <div class="sso-section-head"><div class="lbl">THIẾT LẬP</div><h3>Chuẩn bị cho đội ngũ của bạn</h3><p>Hoàn thành các bước theo thứ tự. Dấu kiểm sẽ cập nhật sau khi hệ thống xác minh từng bước.</p></div>
        <div class="sso-steps">
          <article class="sso-panel sso-step" :class="{'sso-step-done':sso.sso_ready}">
            <div class="sso-step-main">
              <span class="sso-check" :class="{'done':sso.sso_ready}" aria-hidden="true">{{sso.sso_ready?'✓':'1'}}</span>
              <div class="sso-step-copy"><div class="sso-step-title"><h4>Kết nối và kiểm thử SSO doanh nghiệp</h4><span class="sso-step-state">{{sso.sso_ready?'Đã xác minh':'Bước tiếp theo'}}</span></div>
                <p>{{sso.sso_ready?'Một nhân viên đã đăng nhập thành công qua nhà cung cấp doanh nghiệp.':'Kết nối nhà cung cấp của bạn trong WorkOS, sau đó sử dụng liên kết nhân viên để đăng nhập kiểm thử 1 lần.'}}</p>
                <div class="sso-actions">
                  <button class="btn sso-button" :class="!sso.sso_ready?'primary':''" :disabled="!!busy" @click="action('open setup','setup/sso')">
                    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M6.5 2.5h-4v11h11v-4M8 8l5.5-5.5M9.5 2.5h4v4" stroke-linecap="round" stroke-linejoin="round"/></svg>
                    {{sso.sso_ready?'Quản lý kết nối SSO':'Thiết lập SSO doanh nghiệp'}}
                  </button>
                  <button class="btn sso-button" :disabled="!!busy" @click="copyEmployeeLink">
                    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><rect x="5" y="5" width="8" height="8" rx="1.5"/><path d="M3 10H2.5A1.5 1.5 0 0 1 1 8.5v-6A1.5 1.5 0 0 1 2.5 1h6A1.5 1.5 0 0 1 10 2.5V3" stroke-linecap="round"/></svg>
                    Sao chép liên kết nhân viên
                  </button>
                </div>
                <button class="sso-text-action sso-invite-toggle" :aria-expanded="showInviteIT" @click="showInviteIT=!showInviteIT">{{showInviteIT?'Ẩn lời mời IT':'Người khác quản lý nhà cung cấp danh tính? Mời quản trị IT của bạn'}} <span aria-hidden="true">{{showInviteIT?'↑':'↓'}}</span></button>
                <div v-if="showInviteIT" class="sso-invite"><p>WorkOS sẽ gửi email hướng dẫn thiết lập tới quản trị viên IT của bạn.</p><div class="field sso-invite-form"><input v-model="itEmail" type="email" autocomplete="email" aria-label="Email quản trị IT" placeholder="it@company.com" @keyup.enter="inviteIT"/><button class="btn sso-button" :disabled="!!busy" @click="inviteIT">Gửi thư mời <span aria-hidden="true">→</span></button></div></div>
              </div>
            </div>
          </article>

          <article v-if="directoryPlan" class="sso-panel sso-step" :class="{'sso-step-done':sso.directory_ready}">
            <div class="sso-step-main"><span class="sso-check" :class="{'done':sso.directory_ready}" aria-hidden="true">{{sso.directory_ready?'✓':'2'}}</span><div class="sso-step-copy">
              <div class="sso-step-title"><h4>Kết nối Directory Sync</h4><span class="sso-step-state">{{sso.directory_ready?'Đã kết nối':'Chưa kết nối'}}</span></div>
              <p>{{sso.directory_ready?'Thay đổi nhân sự giờ đây có thể tự động cập nhật quyền trong hệ thống.':'Kết nối danh bạ nhân viên để tự động thu hồi quyền truy cập và khóa khi nhân viên rời đi.'}}</p>
              <button class="btn sso-button" :class="sso.sso_ready && !sso.directory_ready?'primary':''" :disabled="!!busy" @click="action('open setup','setup/dsync')"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M6.5 2.5h-4v11h11v-4M8 8l5.5-5.5M9.5 2.5h4v4" stroke-linecap="round" stroke-linejoin="round"/></svg>{{sso.directory_ready?'Quản lý danh bạ':'Thiết lập Directory Sync'}}</button>
            </div></div>
          </article>

          <article class="sso-panel sso-step" :class="{'sso-step-done':sso.enforced}">
            <div class="sso-step-main"><span class="sso-check" :class="{'done':sso.enforced}" aria-hidden="true">{{sso.enforced?'✓':setupStepCount}}</span><div class="sso-step-copy">
              <div class="sso-step-title"><h4>Bắt buộc dùng SSO cho đội ngũ</h4><span class="sso-step-state">{{sso.enforced?'Đang bật':'Đang tắt'}}</span></div>
              <p>{{sso.enforced?'Thành viên bắt buộc phải sử dụng SSO doanh nghiệp để truy cập đội ngũ. Chủ sở hữu vẫn giữ đăng nhập thông thường để khôi phục.':'Sau khi đăng nhập kiểm thử thành công, hãy bắt buộc đăng nhập SSO cho các thành viên. Chủ sở hữu vẫn giữ đăng nhập thông thường.'}}</p>
              <p v-if="directoryPlan && !sso.directory_ready && sso.sso_ready" class="sso-step-hint">Hoàn tất Directory Sync trước nếu bạn muốn tự động thu hồi quyền nhân viên khi nghỉ việc.</p>
              <button class="btn sso-button" :class="sso.sso_ready && (!directoryPlan || sso.directory_ready) && !sso.enforced?'primary':''" :disabled="!!busy || (!sso.sso_ready && !sso.enforced)" @click="action('enforce','enforce',{enabled:!sso.enforced})"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M8 1.5 13 3v4.3c0 3.1-2 5.3-5 7.2-3-1.9-5-4.1-5-7.2V3l5-1.5Z" stroke-linejoin="round"/><path d="m5.8 7.9 1.5 1.5 3-3" stroke-linecap="round" stroke-linejoin="round"/></svg>{{sso.enforced?'Cho phép đăng nhập thông thường':'Bắt buộc dùng SSO'}}</button>
              <span v-if="!sso.sso_ready" class="sso-step-hint">Vui lòng hoàn thành bước đăng nhập kiểm thử trước.</span>
            </div></div>
          </article>
        </div>

        <div v-if="blockedMembers.length" class="sso-panel sso-blocked"><h3>Nhân viên đã bị quản trị viên xóa khỏi đội ngũ</h3><p class="sso-muted">Họ không thể tham gia lại qua SSO cho đến khi bạn cho phép lại.</p><div v-for="member in blockedMembers" :key="member.user_id" class="sso-blocked-row"><span>{{member.email}}</span><button class="btn sm" :disabled="!!busy" @click="restoreMember(member.user_id)">Cho phép SSO lại</button></div></div>
      </template>
    </template>
  </section>
</template>

<style scoped>
.sso-page{width:100%;margin:8px 0 40px;display:grid;gap:18px}
.sso-heading{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;padding:4px 2px 2px}
.sso-heading h2{font-size:28px;letter-spacing:-.04em;line-height:1.1;margin:7px 0 8px}
.sso-heading p,.sso-section-head p{max-width:650px;margin:0;color:var(--muted);line-height:1.5;font-size:13px}
.sso-progress{flex:none;font-size:12px;font-weight:650;color:var(--muted);padding-bottom:3px}
.sso-panel{background:var(--surface,var(--panel));border:1px solid var(--line);border-radius:18px;padding:22px;box-shadow:var(--shadow-sm)}
.sso-panel h3,.sso-section-head h3{font-size:19px;letter-spacing:-.025em;margin:5px 0 6px}
.sso-muted,.sso-step-copy p{color:var(--muted);font-size:13px;line-height:1.5;margin:0}
.sso-plan-summary{display:flex;align-items:flex-start;justify-content:space-between;gap:20px}
.sso-pill{display:inline-flex;align-items:center;white-space:nowrap;border:1px solid var(--line);border-radius:999px;padding:5px 10px;font-size:11px;font-weight:650;background:var(--panel2)}
.sso-pill-ok{color:var(--green);border-color:color-mix(in srgb,var(--green) 28%,var(--line));background:color-mix(in srgb,var(--green) 7%,var(--surface,var(--panel)))}
.sso-pill-warn{color:var(--accent);border-color:color-mix(in srgb,var(--accent) 25%,var(--line))}
.sso-payment-note{background:color-mix(in srgb,var(--accent) 8%,var(--surface,var(--panel)));border:1px solid color-mix(in srgb,var(--accent) 20%,var(--line));border-radius:10px;padding:11px 13px;font-size:12px;line-height:1.5;margin:18px 0 0}
.sso-plan-foot{border-top:1px solid var(--line);padding-top:14px;margin-top:20px;display:flex;justify-content:space-between;align-items:center;gap:12px;color:var(--muted);font-size:12px;line-height:1.5}
.sso-text-action{font:inherit;color:var(--ink);background:none;border:0;padding:3px 0;text-decoration:underline;text-underline-offset:3px;cursor:pointer;text-align:left}
.sso-text-action:hover{color:var(--accent)}.sso-text-action:disabled{opacity:.5;cursor:not-allowed}
.sso-section-head{padding:10px 2px 0}.sso-section-head h3{margin:7px 0 6px}
.sso-steps{display:grid;gap:12px}.sso-step{padding:20px 22px}.sso-step-done{border-color:color-mix(in srgb,var(--green) 28%,var(--line))}
.sso-step-main{display:flex;align-items:flex-start;gap:16px}.sso-check{width:28px;height:28px;flex:none;display:grid;place-items:center;border:1.5px solid var(--line);border-radius:7px;color:var(--muted);font-size:12px;font-weight:700;background:var(--panel2)}
.sso-check.done{border-color:var(--green);background:var(--green);color:var(--onAccent,#fff)}
.sso-step-copy{min-width:0;flex:1}.sso-step-title{display:flex;justify-content:space-between;align-items:baseline;gap:12px}.sso-step-title h4{font-size:15px;letter-spacing:-.01em;margin:2px 0 5px}.sso-step-state{font-size:11px;font-weight:650;color:var(--muted);white-space:nowrap}.sso-step-done .sso-step-state{color:var(--green)}
.sso-actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}.sso-button{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:36px}.sso-button svg{width:15px;height:15px;flex:none}
.sso-step-copy>.sso-button{margin-top:14px}.sso-step-hint{display:inline-block;margin:10px 0 0 10px;color:var(--muted);font-size:11px}.sso-step-copy p.sso-step-hint{display:block;margin:9px 0 0;font-size:11px}
.sso-invite-toggle{margin-top:16px;font-size:12px}.sso-invite{margin-top:9px;padding:14px;background:var(--panel2);border:1px solid var(--line);border-radius:10px}.sso-invite p{margin:0 0 9px}.sso-invite-form{display:flex;gap:8px}.sso-invite-form input{min-width:0;flex:1}
.sso-plan-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:12px}.sso-plan{display:flex;flex-direction:column;gap:12px}.sso-plan-top{display:flex;justify-content:space-between;align-items:center}.sso-plan-mark{font-size:24px;line-height:1}.sso-plan h4{font-size:18px;margin:0}.sso-plan .sso-muted{min-height:58px}.sso-price{margin-top:auto;display:flex;align-items:baseline;gap:5px}.sso-price strong{font-size:26px;letter-spacing:-.04em}.sso-price span{font-size:12px;color:var(--muted)}.sso-plan>.sso-button{margin-top:4px}
.sso-blocked h3{margin-top:0}.sso-blocked-row{display:flex;align-items:center;justify-content:space-between;gap:12px;border-top:1px solid var(--line);padding-top:12px;margin-top:12px;font-size:13px}
@media(max-width:620px){.sso-heading,.sso-plan-summary,.sso-plan-foot{align-items:flex-start;flex-direction:column}.sso-panel{padding:17px}.sso-step-main{gap:12px}.sso-step-title{align-items:flex-start;flex-direction:column;gap:0}.sso-actions,.sso-invite-form{flex-direction:column;align-items:stretch}.sso-actions .sso-button,.sso-invite-form .sso-button{width:100%}.sso-step-hint{display:block;margin:9px 0 0}}
</style>
