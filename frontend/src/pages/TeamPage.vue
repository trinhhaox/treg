<script>
import { useDashboard } from '../state/context'
import { t } from '../state/i18n'
import InfoTip from '../components/ui/InfoTip.vue'
import Money from '../components/ui/Money.vue'
import Avatar from '../components/ui/Avatar.vue'
import TeamShowcase from './team/TeamShowcase.vue'
import TeamAvatar from './team/TeamAvatar.vue'
import EnterpriseSSO from '../components/EnterpriseSSO.vue'
import { NO_KEY } from '../state/constants.js'
import stripeSlate from '../assets/stripe-wordmark-slate.svg'
import stripeWhite from '../assets/stripe-wordmark-white.svg'
// The new agent's check-in poll lives as long as this page (state/agents.js).
export default {
  components: { InfoTip, Money, Avatar, TeamShowcase, TeamAvatar, EnterpriseSSO },
  data: () => ({ NO_KEY, stripeSlate, stripeWhite, memberSsoReady: false }),
  setup: useDashboard,
  mounted() { this.resumeCredentialIssue(); this.resumeAgentPoll(); this.loadMemberSso() },
  watch: {
    activeOrgId() { this.loadMemberSso() },
    orgTab(tab) { if (tab === 'sso' && this.activeRole !== 'owner') this.loadMemberSso() },
  },
  methods: {
    async copyMemberSsoLink() {
      const url = new URL(`/auth/sso/${encodeURIComponent(this.activeOrg.slug)}/start`, location.origin).href
      this.orgMsg = await this.toClipboard(url) ? 'Đã sao chép liên kết đăng nhập cho nhân viên.' : 'Không thể sao chép liên kết đăng nhập.'
    },
    async loadMemberSso() {
      this.memberSsoReady = false
      if (!this.activeOrgId || this.activeRole === 'owner') return
      const orgId = this.activeOrgId
      const status = await this.api(`/orgs/${orgId}/sso`).catch(() => null)
      if (this.activeOrgId !== orgId || this.activeRole === 'owner') return
      this.memberSsoReady = !!(status?.sso_ready && ['active', 'trialing', 'past_due'].includes(status.subscription_status))
      if (!this.memberSsoReady && this.orgTab === 'sso') this.orgTab = 'keys'
    },
  },
  beforeUnmount() { this.parkCredentialIssue() },
}
</script>

<template>

          <div class="tut-head">
            <Avatar v-if="activeOrg && activeOrg.avatar_url" :src="activeOrg.avatar_url" :name="activeName" :size="40" />
            <div><h1>{{t('team.title', {name: activeName})}}<span v-if="isPersonal(activeOrg)" class="chip" style="margin-left:8px;vertical-align:middle">{{t('common.personal')}}</span></h1>
              <p class="sub" style="margin:0">{{t('team.role_desc', {role: activeRole})}} <span class="muted">Chuyển đổi, tạo mới hoặc tham gia đội ngũ từ menu ở đầu trang.</span></p>
              <div style="display:flex;gap:8px;align-items:center;margin-top:8px">
                <button class="btn sm primary" @click="agentConnectDialog=true">{{t('mcp.nav_btn')}}</button>
                <button v-if="activeRole!=='owner' && memberSsoReady" class="btn sm" @click="copyMemberSsoLink">Sao chép liên kết SSO công ty</button>
              </div>
            </div>
          </div>
          <!-- settings for the ACTIVE team (switching lives in the sidebar) -->
          <div v-if="activeOrg" style="margin-top:20px">
            <div class="tabs" style="margin:4px 0 16px">
              <button v-if="canAdmin" :class="{active:orgTab==='members'}" @click="orgTab='members'">{{t('team.tab_members')}}</button>
              <button :class="{active:orgTab==='keys'}" @click="orgTab='keys'; loadApiKeys(); loadApiKeySpend()">{{t('team.tab_keys')}}</button>
              <button v-if="canAdmin" :class="{active:orgTab==='projects'}" @click="orgTab='projects'">{{t('team.tab_projects')}}</button>
              <button v-if="canAdmin" :class="{active:orgTab==='policy'}" @click="orgTab='policy'">{{t('team.tab_policy')}}</button>
              <button v-if="canAdmin" :class="{active:orgTab==='billing'}" @click="orgTab='billing'">{{t('team.tab_billing')}}</button>
              <button v-if="canAdmin" :class="{active:orgTab==='showcase'}" @click="orgTab='showcase'">{{t('team.tab_showcase')}}</button>
              <button v-if="activeRole==='owner' || memberSsoReady" :class="{active:orgTab==='sso'}" @click="orgTab='sso'">{{t('team.tab_sso')}}</button>
              <button :class="{active:orgTab==='danger'}" @click="orgTab='danger'; resetRenameForm()">{{t('team.tab_settings')}}</button>
            </div>
            <p v-if="!canAdmin && !['keys','danger','sso'].includes(orgTab)" class="sub" style="margin-bottom:12px">Thành viên, dự án và chính sách chỉ hiển thị cho quản trị viên.</p>
            <div v-if="memberFunds && !canAdmin" class="tut-notice" role="status" style="margin-bottom:12px;display:flex;justify-content:space-between;gap:12px;align-items:flex-start">
              <span>Nếu đội ngũ của bạn hết tiền, hãy liên hệ quản trị viên để nạp thêm<template v-if="teamAdmins && teamAdmins.length">: <b>{{teamAdmins.map(a=>a.email).join(', ')}}</b></template>. Chỉ quản trị viên mới có quyền xem mục Thanh toán.</span>
              <button class="btn sm ico" @click="memberFunds=false" aria-label="Đóng">✕</button>
            </div>
            <p v-if="myUsage && myUsage.cap>=0" class="sub" style="margin:-6px 0 12px">Lượt dùng của bạn hôm nay: <b>{{myUsage.used_today}} / {{myUsage.cap}}</b> lượt gọi.</p>
            <div v-if="orgErr" class="banner">{{orgErr}}</div>
            <div v-if="billingNote && canAdmin" class="tut-notice" role="status" style="margin-bottom:12px;display:flex;justify-content:space-between;gap:12px;align-items:flex-start">
              <span>{{billingNote}}</span><button class="btn sm ico" @click="billingNote=''" aria-label="Đóng">✕</button>
            </div>
            <div v-if="orgMsg" class="tut-notice" style="margin-bottom:12px;display:flex;justify-content:space-between;gap:12px;align-items:flex-start">
              <span>{{orgMsg}}</span><button class="btn sm ico" @click="orgMsg=''" aria-label="Đóng">✕</button>
            </div>
            <EnterpriseSSO v-if="orgTab==='sso' && (activeRole==='owner' || memberSsoReady)" :org-id="activeOrg.org_id" :slug="activeOrg.slug" :owner="activeRole==='owner'" />
            <div v-if="credentialIssue" class="tut-notice" role="status" style="margin-bottom:12px">
              <template v-if="credentialIssue.status==='pending'">Yêu cầu tạo khóa đang được xử lý. Bạn có thể chuyển đội ngũ và quay lại đây nhận kết quả. Vui lòng giữ tab trình duyệt này.</template>
              <template v-else-if="credentialIssue.status==='checking'">Đang kiểm tra khóa vừa phát hành…</template>
              <template v-else-if="credentialIssue.error">{{credentialIssue.error}}</template>
              <template v-else>Hãy lưu khóa này trước khi tạo khóa khác. Khóa chỉ lưu trong tab trình duyệt này cho đến khi bạn đóng thẻ khóa.</template>
              <button v-if="credentialIssue.status==='held'" class="btn sm" @click="resumeCredentialIssue">Kiểm tra trạng thái khóa</button>
              <button v-if="credentialIssue.status==='ready' && orgTab!==(credentialIssue.type==='agent'?'members':'keys')" class="btn sm" @click="orgTab=credentialIssue.type==='agent'?'members':'keys'">Mở khóa vừa tạo</button>
              <button v-if="['failed','unavailable'].includes(credentialIssue.status)" class="btn sm" @click="dismissCredentialIssue">Bỏ qua</button>
            </div>

            <template v-if="canAdmin && orgTab==='members'">
              <div v-if="agentErr" class="banner" style="margin-top:8px">{{agentErr}}</div>
          <!-- the token is shown ONCE: make that unmissable -->
          <div v-if="newAgent || snipAgent" class="card" style="margin-top:16px" :style="newAgent?'border-color:var(--accent)':''">
            <div class="lbl" style="margin-top:0;display:flex;align-items:center;gap:10px">
              <template v-if="newAgent">Token cho {{newAgent.name}} — hãy sao chép ngay</template>
              <template v-else>Cách sử dụng {{snipAgent.name}}</template>
              <button v-if="!newAgent" class="btn sm" style="margin-left:auto" @click="snipAgent=null">Đóng</button>
            </div>
            <p v-if="newAgent && newAgent.rotated" class="tut-notice" style="margin:2px 0 10px"><b>Khóa trước đó đã ngừng hoạt động ngay lập tức.</b> Hãy cập nhật <b>{{newAgent.name}}</b> ở mọi nơi đang chạy trước khi đóng thẻ này.</p>
            <p v-if="newAgent" class="sub" style="margin:2px 0 10px">Lưu khóa này trước khi đóng thẻ hoặc tab trình duyệt. Gán vào biến môi trường <code>TREG_TOKEN</code> của Agent. Bất kỳ ai có khóa này đều có thể đại diện cho {{newAgent.name}}, hãy bảo mật tuyệt đối và không commit vào mã nguồn.
              <span v-if="agentConnected" class="chip ok" style="margin-left:8px">✓ đã kết nối — {{newAgent.name}} đã gọi thành công</span>
              <span v-else class="muted" style="margin-left:8px">đang chờ lượt kết nối đầu tiên…</span></p>
            <p v-else class="sub" style="margin:2px 0 10px">Máy chủ chỉ lưu mã băm của token nên không thể hiển thị lại — các đoạn mã này sử dụng <span class="mono">$TREG_TOKEN</span>. <button class="btn sm" :disabled="!!credentialIssue" @click="rotateAgent(snipAgent,true)">⟳ Đổi khóa &amp; điền token thật</button> <span class="muted">(khóa cũ sẽ ngừng hoạt động)</span></p>
            <div v-if="newAgent" class="field">
              <input :value="newAgent.token" readonly style="font-family:var(--mono)" @focus="$event.target.select()"/>
              <button class="btn primary" @click="copy(newAgent.token,'agenttok')">{{copied==='agenttok'?'Đã chép':'Sao chép'}}</button>
              <button class="btn" @click="dismissCredentialIssue">{{newAgent.rotated?'Đã cập nhật '+newAgent.name:'Xong'}}</button>
            </div>
            <div class="tabs" style="margin:14px 0 8px">
              <button :class="{active:agentSnip==='prompt'}" @click="agentSnip='prompt'">Gửi cho Agent của bạn</button>
              <button :class="{active:agentSnip==='env'}" @click="agentSnip='env'">Biến môi trường (.env)</button>
            </div>
            <div class="lc-codewrap">
              <button class="lc-cp" @click="copy(agentSnippet,'agentsnip')">{{copied==='agentsnip'?'✓ đã chép':'sao chép'}}</button>
              <pre style="max-height:220px;overflow:auto">{{agentSnippet}}</pre>
            </div>
            <p class="sub" style="margin:6px 0 0;font-size:11.5px">Đặt đoạn này ở bất kỳ đâu Agent chạy — trong file <span class="mono">.env</span>, CI secret hoặc file cấu hình.</p>
          </div>

              <div class="lbl" style="margin-top:14px">Thành viên</div>
              <p class="sub" style="margin:-2px 0 8px;font-size:12px">Hạn mức ngày = số lượt gọi API + lệnh chạy tối đa mỗi ngày của một thành viên. Để trống nếu không giới hạn.</p>
              <p class="sub" style="margin:-2px 0 8px;font-size:12px"><b>Công cụ</b> = những endpoint/CLI thành viên được phép gọi hoặc chạy. <b>Chạy local</b> = được phép chạy CLI trên máy riêng (tắt = chỉ chạy trên server). Chủ sở hữu luôn có toàn quyền.</p>
              <table>
                <tr><th>Email</th><th>Vai trò</th><th style="text-align:right">Hôm nay</th><th>Hạn mức ngày</th><th>Công cụ</th><th>Chạy local</th><th></th></tr>
                <!-- An empty roster under its header read as "no members" until the request answered. -->
                <tr v-if="!orgMembersLoaded"><td colspan="7" class="muted">Đang tải danh sách thành viên…</td></tr>
                <template v-for="m in rosterMembers" :key="m.key">
                <tr v-if="m.is_observed">
                  <td><span style="opacity:.45">↳</span> <b>{{m.client}}</b> <span class="chip" title="nhận diện qua lưu lượng truy cập">phát hiện</span>
                    <div class="muted" style="font-size:11px">chạy dưới quyền {{short(m.member)}} — kế thừa toàn bộ quyền truy cập</div></td>
                  <td><span class="muted" style="font-size:12px">—</span></td>
                  <td style="text-align:right" class="muted">{{m.used_today}}</td>
                  <td colspan="3"><span class="muted" style="font-size:12px">{{m.calls_30d}} lượt gọi trong 30 ngày · thấy lần cuối {{when(m.last_seen)}}</span></td>
                  <td style="text-align:right"><button class="btn sm" @click="promoteObserved(m)" title="cấp token riêng cho runtime này">Giới hạn quyền cho Agent này</button></td>
                </tr>
                <tr v-else>
                  <td>
                    <template v-if="m.is_agent"><span style="opacity:.45">↳</span> <b>{{m.name}}</b> <span class="chip" :title="m.email">agent</span>
                      <div class="muted" style="font-size:11px">{{m.created_by?('tạo bởi '+short(m.created_by)):'danh tính máy'}}</div>
                      <div v-if="confirmAgent==='rotate-'+m.user_id" class="sub" style="font-size:11px;margin-top:5px;max-width:360px"><b>Khóa hiện tại sẽ dừng ngay lập tức.</b> Thẻ tiếp theo sẽ hiển thị khóa thay thế một lần duy nhất để bạn cập nhật cho {{m.name}}.</div>
                      <div v-if="confirmAgent==='revoke-'+m.user_id" class="sub" style="font-size:11px;margin-top:5px;max-width:360px"><b>Thao tác này sẽ xóa Agent và thu hồi toàn bộ khóa.</b> Lịch sử hoạt động vẫn được lưu trữ kiểm toán.</div></template>
                    <span v-else style="display:inline-flex;gap:8px;align-items:center"><Avatar :src="m.avatar_url" :name="m.email" :size="22" round />{{m.email}}</span>
                  </td>
                  <td>
                    <select v-if="isOwner" class="msel" :value="m.role" @change="setRole(m,$event.target.value)">
                      <option v-for="r in ['viewer','member','admin','owner']" :key="r" :value="r">{{r}}</option>
                    </select>
                    <span v-else class="role" :class="m.role">{{m.role}}</span>
                  </td>
                  <td style="text-align:right" class="muted">{{m.used_today}}</td>
                  <td><input class="msel" type="number" min="0" step="1" style="width:78px" :value="capField(m.daily_call_cap)" placeholder="Không giới hạn" @change="setCap(m,$event.target.value)" :aria-label="'Hạn mức ngày cho '+(m.email||m.name)" title="Trống = không giới hạn"/></td>
                  <td>
                    <span v-if="m.role==='owner'" class="chip">Toàn bộ</span>
                    <button v-else class="btn sm" :class="{active:editAccess===m.user_id}" @click="openAccess(m)" :title="m.tool_access===null?'Truy cập mọi công cụ':'Truy cập '+m.tool_access.length+' công cụ'">{{m.tool_access===null?'Toàn bộ':m.tool_access.length+' công cụ'}} ▾</button>
                  </td>
                  <td>
                    <label class="tgl" :title="m.role==='owner'?'chủ sở hữu luôn được chạy local':(m.local_run_enabled?'chạy local đang bật — bấm để tắt':'chạy local đang tắt — chỉ chạy trên server')">
                      <input type="checkbox" :checked="m.local_run_enabled" :disabled="m.role==='owner'" @change="setLocalRun(m,$event.target.checked)"/>
                      <span>{{m.local_run_enabled?'bật':'tắt'}}</span>
                    </label>
                  </td>
                  <td style="text-align:right;white-space:nowrap">
                    <template v-if="m.is_agent">
                      <span class="row-actions"><button class="btn sm" @click="showAgentSetup(m)" title="hướng dẫn cấp danh tính cho agent">{{t('team.setup')}}</button>
                      <button class="btn sm" :disabled="!!credentialIssue" :class="{danger:confirmAgent==='rotate-'+m.user_id}" @click="rotateAgent(m)" title="tạo token mới — token cũ ngừng hoạt động ngay">{{confirmAgent==='rotate-'+m.user_id?t('team.rotate_confirm'):t('team.rotate')}}</button>
                      <button class="btn sm" :class="{danger:confirmAgent==='revoke-'+m.user_id}" @click="revokeAgent(m)">{{confirmAgent==='revoke-'+m.user_id?t('team.revoke_confirm'):t('team.revoke')}}</button></span>
                    </template>
                    <button v-else-if="m.role!=='owner'" class="btn sm" :class="{danger:confirmRemove===m.user_id}" @click="removeMember(m)">{{confirmRemove===m.user_id?t('team.remove_member_confirm'):t('team.remove_member')}}</button>
                  </td>
                </tr>
                <tr v-if="!m.is_observed && editAccess===m.user_id">
                  <td colspan="7" style="background:color-mix(in srgb,var(--accent) 5%,transparent)">
                    <div style="padding:6px 2px">
                      <div class="sub" style="margin-bottom:6px">Công cụ &amp; skills <b>{{m.email}}</b> được phép dùng — bỏ chọn để thu hồi. Chọn tất cả = toàn quyền (và công cụ mới sẽ tự động cấp quyền).</div>
                      <div v-if="!accessNames.length" class="muted" style="font-size:12px">Chưa có công cụ nào được đăng ký.</div>
                      <div style="display:flex;flex-wrap:wrap;gap:6px 16px">
                        <label v-for="n in accessNames" :key="n" class="tgl" style="min-width:150px">
                          <input type="checkbox" v-model="accessDraft[n]"/><span>{{n}}</span>
                        </label>
                      </div>
                      <template v-if="projects.length">
                        <div class="sub" style="margin:12px 0 6px">Dự án <b>{{m.email}}</b> được phép truy cập — chọn tất cả = mọi dự án. Công cụ không thuộc dự án nào sẽ hiển thị với tất cả mọi người.</div>
                        <div style="display:flex;flex-wrap:wrap;gap:6px 16px">
                          <label v-for="p in projects" :key="p.id" class="tgl" style="min-width:150px">
                            <input type="checkbox" v-model="projDraft[p.id]"/><span>{{p.name}}</span>
                          </label>
                        </div>
                      </template>
                      <p v-else class="sub" style="margin:12px 0 0;font-size:12px">Gợi ý: tạo một <a href="#" @click.prevent="orgTab='projects'">dự án</a> để phân chia quyền hạn công cụ theo nhóm.</p>
                      <div style="margin-top:10px;display:flex;gap:8px">
                        <button class="btn sm primary" @click="saveAccess(m)">{{t('team.save_access')}}</button>
                        <button class="btn sm" @click="editAccess=null">{{t('common.cancel')}}</button>
                        <button class="btn sm" @click="setAllAccess(true)">{{t('team.check_all')}}</button>
                        <button class="btn sm" @click="setAllAccess(false)">{{t('team.uncheck_all')}}</button>
                      </div>
                    </div>
                  </td>
                </tr>
                </template>
              </table>

              <div class="lbl" style="margin-top:22px;display:flex;align-items:center;gap:10px">Thêm vào đội ngũ
                <button v-if="!isPersonal(activeOrg)" class="btn sm" :class="{active:showInvite}" @click="showInvite=!showInvite; if(showInvite)showAddAgent=false">{{t('team.add_member')}}</button>
                <button class="btn sm" :class="{active:showAddAgent}" @click="openAddAgent()">{{t('team.add_agent')}}</button></div>
              <p class="sub" style="margin:-2px 0 8px;font-size:12px">Thành viên là người dùng đăng nhập. Agent là danh tính máy có token riêng — có hạn mức, phạm vi truy cập và nhật ký riêng. Phân quyền qua <b>Công cụ</b> và <b>Dự án</b> ở trên.</p>
              <div v-show="showAddAgent">
          <div class="lbl" style="margin-top:18px">Agent mới</div>
          <p v-if="promoteHint" class="sub" style="margin:-2px 0 6px;font-size:12px;color:var(--accent)">{{promoteHint}}</p>
          <div class="field" style="max-width:620px">
            <input v-model="agentName" placeholder="tên-agent (vd: ci-bot)" @keyup.enter="createAgent"/>
            <select v-model="agentRole" class="msel"><option>viewer</option><option>member</option><option v-if="isOwner">admin</option></select>
            <input :value="capField(agentCap)" @input="agentCap=capValue($event.target.value)" type="number" min="0" step="1" class="msel" style="width:96px" placeholder="Không giới hạn" aria-label="Hạn mức gọi ngày" title="Hạn mức gọi ngày; để trống = không giới hạn"/>
            <button class="btn primary" @click="createAgent" :disabled="agentBusy||!!credentialIssue||!agentAccessMode">{{agentBusy?'…':'Tạo Agent'}}</button>
          </div>
          <div style="max-width:620px;margin:4px 0 8px">
            <div style="display:flex;gap:16px;align-items:center;flex-wrap:wrap">
              <span class="sub" style="font-size:12px"><b>Công cụ:</b></span>
              <label class="tgl"><input type="radio" value="all" v-model="agentAccessMode"/><span>Tất cả công cụ</span></label>
              <label class="tgl"><input type="radio" value="choose" v-model="agentAccessMode"/><span>Chọn công cụ</span></label>
              <span v-if="!agentAccessMode" class="sub" style="font-size:11px;color:var(--accent)">Vui lòng chọn quyền truy cập trước khi tạo.</span>
            </div>
            <div v-if="agentAccessMode==='choose'" style="display:flex;flex-wrap:wrap;gap:6px 16px;margin-top:7px">
              <span v-if="!accessNames.length" class="muted" style="font-size:12px">Chưa có công cụ nào; Agent này sẽ không có quyền truy cập công cụ nào.</span>
              <label v-for="n in accessNames" :key="n" class="tgl" style="min-width:150px"><input type="checkbox" v-model="agentToolSel[n]"/><span>{{n}}</span></label>
            </div>
          </div>
          <div v-if="projects.length" style="max-width:620px;margin:4px 0 0;display:flex;gap:6px 16px;flex-wrap:wrap;align-items:center">
            <span class="sub" style="font-size:12px">Dự án (chọn tất cả = mọi dự án):</span>
            <label v-for="p in projects" :key="p.id" class="tgl"><input type="checkbox" v-model="agentProjSel[p.id]"/><span>{{p.name}}</span></label>
          </div>
          <p class="sub" style="margin:-2px 0 0;font-size:12px">Để trống hạn mức nghĩa là không giới hạn. Agent không thể là chủ sở hữu và không thể đăng nhập trực tiếp; token là cách duy nhất để gọi dưới danh tính của nó.</p>

              </div>
              <template v-if="!isPersonal(activeOrg)">
              <div v-show="showInvite">
              <div class="field" style="max-width:560px">
                <input v-model="inviteEmail" type="email" placeholder="dongnghiep@email.com" @keyup.enter="sendInvite"/>
                <select v-model="inviteRole" class="msel"><option>viewer</option><option>member</option><option v-if="isOwner">admin</option></select>
                <button class="btn primary" @click="sendInvite" :disabled="orgBusy">{{orgBusy?'…':'Mời'}}</button>
              </div>
              <div style="max-width:560px;margin:-4px 0 4px;display:flex;gap:16px;align-items:center;flex-wrap:wrap">
                <label class="tgl"><input type="radio" :checked="!inviteCustomize" @change="inviteCustomize=false"/><span>Tất cả công cụ</span></label>
                <label class="tgl"><input type="radio" :checked="inviteCustomize" @change="openInviteCustomize()"/><span>Tùy chỉnh</span></label>
                <label class="tgl"><input type="checkbox" v-model="inviteLocalRun"/><span>Cho phép chạy local</span></label>
              </div>
              <div v-if="inviteCustomize" style="max-width:560px;margin-bottom:8px">
                <div class="sub" style="font-size:12px;margin-bottom:4px">Công cụ thành viên này được phép dùng:</div>
                <div v-if="!tools.length" class="muted" style="font-size:12px">Chưa có công cụ nào.</div>
                <div style="display:flex;flex-wrap:wrap;gap:6px 16px">
                  <label v-for="n in accessNames" :key="n" class="tgl" style="min-width:150px"><input type="checkbox" v-model="inviteToolSel[n]"/><span>{{n}}</span></label>
                </div>
              </div>
              <div v-if="lastInvite" class="tut-notice" style="max-width:560px">
                Lời mời đã gửi tới <b>{{lastInvite.email}}</b> ({{lastInvite.role}}). Họ có thể đăng nhập để chấp nhận ngay - hoặc dùng mã một lần này:
                <div style="display:flex;gap:8px;align-items:center;margin-top:6px"><code class="mono" style="word-break:break-all;font-size:11px">{{lastInvite.code}}</code><button class="btn sm" @click="copy(lastInvite.code)">{{copied?'✓ đã chép':'⧉ sao chép'}}</button></div>
              </div>

              <div class="lbl" style="margin-top:18px">Lời mời đang chờ</div>
              <table v-if="orgInvites.length">
                <tr><th>Email</th><th>Vai trò</th><th>Người mời</th><th>Hết hạn</th><th></th></tr>
                <tr v-for="inv in orgInvites" :key="inv.id">
                  <td>{{inv.email}}</td><td><span class="role" :class="inv.role">{{inv.role}}</span></td>
                  <td class="muted">{{short(inv.invited_by)}}</td><td class="muted">{{inv.expires_at?until(inv.expires_at):'không bao giờ'}}</td>
                  <td style="text-align:right"><button class="btn sm" @click="revokeInvite(inv)">Thu hồi</button></td>
                </tr>
              </table>
              <p v-else class="sub">Không có lời mời nào đang chờ.</p>
              </div>
              </template>
            </template>

            <!-- API KEYS tab. Members see their own keys; admins see the full team inventory. -->
            <template v-if="orgTab==='keys'">
              <div class="tut-head" style="align-items:flex-end;margin-bottom:14px"><div><div class="lbl">Khóa API</div>
                <p class="sub" style="margin:2px 0 0">Sử dụng nhiều khóa mà không cần tạo thêm thành viên. Phân quyền, hạn mức và thanh toán vẫn gắn liền với danh tính tương ứng.</p></div></div>
              <div v-if="keyErr" class="banner">{{keyErr}}</div>
              <div v-if="keyMsg" class="tut-notice" style="margin-bottom:12px;display:flex;justify-content:space-between;gap:12px;align-items:flex-start">
                <span>{{keyMsg.text}}</span><span style="white-space:nowrap"><button v-if="keyMsg.agent" class="btn sm" @click="orgTab='members'; keyMsg=null">Mở Thành viên</button><button class="btn sm ico" @click="keyMsg=null" aria-label="Đóng">✕</button></span>
              </div>
              <div v-if="newApiKey" class="card" style="border-color:var(--accent);margin-bottom:16px">
                <div class="lbl"><template v-if="newApiKey.kind==='default_human'">Khóa mặc định đã đổi — hãy sao chép khóa mới</template><template v-else-if="newApiKey.assigned_type==='agent'">Khóa mới cho {{newApiKey.assigned_name}}</template><template v-else>{{newApiKey.name}} — hãy sao chép ngay</template></div>
                <p v-if="newApiKey.kind==='default_human'" class="tut-notice" style="margin:2px 0 10px"><b>Khóa trước đó đã ngừng hoạt động ngay lập tức.</b> Hãy cập nhật mọi CLI, MCP server hoặc ứng dụng đang dùng khóa Mặc định của đội ngũ này.</p>
                <p v-if="newApiKey.assigned_type==='agent' && newApiKey.rotated" class="tut-notice" style="margin:2px 0 10px"><b>Khóa trước đó đã ngừng hoạt động ngay lập tức và bị ẩn khỏi danh sách.</b> Hãy cập nhật {{newApiKey.assigned_name}} ở mọi nơi đang chạy trước khi đóng thẻ này.</p>
                <p class="sub" style="margin:2px 0 10px"><template v-if="newApiKey.kind==='default_human'">Khóa này có thể xem lại tại trang Bắt đầu.</template><template v-else>Máy chủ chỉ lưu mã băm của khóa. Hãy lưu lại khóa trước khi đóng thẻ này hoặc tab trình duyệt.<template v-if="newApiKey.assigned_type==='agent'"> Bất kỳ ai giữ khóa này đều có thể đại diện cho {{newApiKey.assigned_name}}, hãy lưu trong biến môi trường hoặc trình quản lý bí mật.</template></template></p>
                <div class="field"><input :value="newApiKey.secret" readonly class="mono" @focus="$event.target.select()"/><button class="btn primary" @click="copy(newApiKey.secret,'managedkey')">{{copied==='managedkey'?'Đã chép':'Sao chép'}}</button><button class="btn" @click="dismissCredentialIssue">{{newApiKey.assigned_type==='agent'?'Đã cập nhật '+newApiKey.assigned_name:'Xong'}}</button></div>
                <p v-if="newApiKey.kind==='default_human'" class="sub" style="margin:6px 0 0;font-size:11.5px">Người dùng CLI có thể chạy <code>treg login</code> để tự lưu khóa mới.</p>
                <template v-if="newApiKey.assigned_type==='agent'">
                  <p class="sub" style="margin:6px 0 0"><span v-if="agentConnected" class="chip ok">✓ đã kết nối — {{newApiKey.assigned_name}} đã gọi thành công</span><span v-else class="muted">đang chờ lượt kết nối đầu tiên…</span></p>
                  <div class="tabs" style="margin:14px 0 8px"><button :class="{active:agentSnip==='prompt'}" @click="agentSnip='prompt'">Gửi cho Agent của bạn</button><button :class="{active:agentSnip==='env'}" @click="agentSnip='env'">Biến môi trường (.env)</button></div>
                  <div class="lc-codewrap"><button class="lc-cp" @click="copy(agentSnippet,'agentsnip')">{{copied==='agentsnip'?'✓ đã chép':'sao chép'}}</button><pre style="max-height:220px;overflow:auto">{{agentSnippet}}</pre></div>
                  <p class="sub" style="margin:6px 0 0;font-size:11.5px">Thay thế <code>TREG_TOKEN</code> ở mọi môi trường, CI secret hoặc cấu hình nơi {{newApiKey.assigned_name}} đang chạy.</p>
                </template>
              </div>
              <div v-if="activeRole!=='viewer'" class="field" style="max-width:620px;margin-bottom:18px"><input v-model="keyName" :class="{'field-invalid':keyNameInvalid}" :aria-invalid="keyNameInvalid" placeholder="Tên khóa mới" maxlength="80" @input="keyNameInvalid=false" @keyup.enter="createApiKey"/><button class="btn primary" :disabled="keyBusy||!!credentialIssue" @click="createApiKey">{{keyBusy?'…':'Tạo khóa'}}</button></div>
              <template v-for="group in apiKeyGroups" :key="group.identity">
                <div class="lbl" style="margin-top:16px">{{group.name}} <span class="chip">{{group.type}}</span><span v-if="group.type==='agent' && group.name!==group.identity" class="muted mono" style="margin-left:8px;text-transform:none">{{group.identity}}</span></div>
                <table class="key-table"><tr><th>Khóa</th><th>Trạng thái</th><th style="text-align:right" title="Chi phí phát sinh trong 30 ngày qua (UTC), từ sổ cái">Chi tiêu 30 ngày</th><th>Ngày tạo</th><th>Dùng gần nhất</th><th></th></tr>
                  <tr v-for="k in group.rows" :key="k.id">
                    <td class="key-identity"><input v-if="editKey===k.id" v-model="editKeyName" maxlength="80" class="msel" @keyup.enter="renameApiKey(k)"/><template v-else><div class="key-primary"><span v-if="group.type==='human' && k.assigned_type==='agent'" class="muted" aria-hidden="true">↳</span><b>{{group.type==='human' && k.assigned_type==='agent'?k.assigned_name:k.name}}</b><span class="chip">{{keyKind(k.kind)}}</span></div><div class="key-meta mono">{{maskedKey(k)}}</div></template>
                    </td>
                    <td><span class="badge" :class="k.state==='active'?'ok':'invalid'">{{k.state}}</span></td>
                    <td class="key-spend"><Money v-if="keySpend(k)" :micro="keySpend(k).spent_micro" /><span v-else-if="apiKeySpend && !apiKeySpend.ready" class="muted" title="Lịch sử chi tiêu đang được tổng hợp.">Đang tổng hợp…</span><span v-else class="muted">—</span></td>
                    <td class="muted">{{k.created_at?when(k.created_at):'Không rõ'}}</td><td class="muted">{{k.last_used_at?when(k.last_used_at):'Chưa từng'}}</td>
                    <td style="text-align:right;white-space:nowrap"><span v-if="editKey===k.id" class="row-actions"><button class="btn sm primary" @click="renameApiKey(k)">Lưu</button><button class="btn sm" @click="editKey=null">Hủy</button></span><span v-else class="row-actions">
                      <button class="btn sm" @click="showKeyActivity(k)">Hoạt động</button><button v-if="k.can_rotate" class="btn sm" :disabled="!!credentialIssue" @click="requestKeyAction(k,'rotate')">Đổi khóa</button><button v-if="keyHasMore(k)" class="btn sm ico" aria-haspopup="menu" :aria-expanded="keyMenu&&keyMenu.key.id===k.id" :aria-label="'Thao tác khác cho '+k.name" @click.stop="toggleKeyMenu(k,$event)">⋮</button>
                    </span></td>
                  </tr>
                </table>
              </template>
              <template v-if="apiKeySpend && apiKeySpend.ready && apiKeySpend.unattributed && apiKeySpend.unattributed.spent_micro && apiKeys.length">
                <div class="lbl" style="margin-top:16px">{{NO_KEY.title}} <InfoTip :title="NO_KEY.title" :text="NO_KEY.text" /></div>
                <table class="key-table"><tr><td class="key-identity"><span class="muted">Chi phí từ các lượt gọi không gắn khóa API</span></td><td class="key-spend"><Money :micro="apiKeySpend.unattributed.spent_micro" /></td></tr></table>
              </template>
              <p v-if="apiKeySpend && !apiKeySpend.ready && apiKeys.length" class="sub">Lịch sử chi tiêu đang được chuẩn bị. Dữ liệu sẽ hiển thị trong thời gian tới.</p>
              <p v-if="!keyBusy && !apiKeys.length" class="sub">Chưa có khóa API nào.</p>
            </template>

            <!-- BILLING. Balance + top-ups + auto top-up for the ACTIVE team. Admin-gated like the
                 rest of the team tabs. Hidden entirely when the deployment has no Stripe key
                 (self-hosters don't sell balance) - `billing.configured` says so. -->
            <template v-if="canAdmin && orgTab==='billing'">
              <div v-if="billing" style="margin-top:4px">
                <div class="card" style="padding:16px">
                  <div style="display:flex;gap:12px;align-items:flex-start;flex-wrap:wrap">
                    <div style="flex:1;min-width:220px">
                      <div class="lbl">{{t('nav.balance') || 'Số dư'}}</div>
                      <div style="font-size:28px;font-weight:700;color:var(--accent);font-family:var(--mono)">{{money(billing.balance_micro)}}</div>
                    </div>
                    <!-- Stripe's hosted portal: card, billing address, tax ID and the invoice archive.
                         Hidden until the team has a Stripe customer, which its first payment creates. -->
                    <button v-if="billing.portal" class="btn sm" :disabled="billingBusy" @click="openPortal()"
                            title="Cập nhật thẻ, địa chỉ thanh toán, mã số thuế và tải hóa đơn">
                      {{billingBusy?'Đang mở…':'Quản lý thanh toán'}}
                    </button>
                  </div>
                  <p v-if="!billing.configured" class="sub" style="margin:12px 0 0">
                    Tính năng nạp tiền tự động qua thẻ (Stripe) chưa được cấu hình trên máy chủ này.
                    <template v-if="isAdmin">
                      <br><span style="color:var(--accent);font-weight:600">Là Quản trị viên tối cao (SuperAdmin)?</span> <a href="#admin" @click.prevent="go('admin')">Nạp tiền thủ công cho tổ chức tại Trang Quản Trị →</a>
                    </template>
                  </p>

                  <template v-if="billing.configured">
                    <div style="margin-top:12px">
                      <!-- A team that arrived through someone's link does not know a bonus exists.
                           This is the one screen where saying so changes what they do, and the
                           MINIMUM is the part that matters: the first preset ($5) is below it, so
                           without this the most-clicked button silently forfeits the reward. -->
                      <div v-if="billing.referral_offer" style="margin-top:8px;padding:9px 12px;font-size:12.5px;
                           border:1px solid var(--green);border-radius:8px;
                           background:color-mix(in srgb,var(--green) 12%,transparent)">
                        <!-- The referrer is MASKED (`j•••@domain`): a referral link is public, so
                             the full address would be published to every stranger who signs up
                             through an influencer's link. The domain is what a real friend
                             recognises. Falls back to "to treg" if we somehow have no address. -->
                        Bạn được mời
                        <template v-if="billing.referral_offer.referrer_masked">bởi
                          <b>{{billing.referral_offer.referrer_masked}}</b></template>
                        <template v-else>tham gia treg</template>
                        — nạp
                        <b>{{money(billing.referral_offer.remaining_micro)}}</b>
                        <template v-if="billing.referral_offer.topped_up_micro"> nữa</template>
                        <template v-else> trở lên</template>
                        và chúng tôi sẽ cộng ngay <b>{{money(billing.referral_offer.referred_micro)}}</b> vào
                        số dư của bạn <b>ngay lập tức</b>. Người giới thiệu nhận được
                        {{money(billing.referral_offer.referrer_micro)}} sau
                        {{billing.referral_offer.hold_days}} ngày.
                      </div>
                      <!-- The amounts live in a modal (openTopup), not inline: choosing a size,
                           seeing the bonus it earns and deciding on auto top-up are one decision,
                           and the mandate text has to sit next to the Pay button it authorizes. -->
                      <button class="btn primary" :disabled="billingBusy" @click="openTopup()">Nạp tiền</button>
                    </div>

                    <!-- `no_card` is not a failure: consent was recorded (usually from the top-up
                         modal) and the policy arms itself when a payment saves a card. Showing it in
                         the red "switched itself off" banner made an abandoned Checkout look broken. -->
                    <p v-if="billing.autotopup.disabled_reason==='no_card'" class="sub" style="margin:14px 0 0">
                      Tự động nạp tiền đã được thiết lập và sẽ kích hoạt ngay khi bạn nạp tiền và lưu thẻ. Cho đến lúc đó, các lệnh gọi sẽ tạm dừng khi hết số dư.
                    </p>
                    <p v-else-if="billing.autotopup.disabled_reason==='payment_refunded'" class="sub" style="margin:14px 0 0">
                      Tự động nạp tiền đang tắt do khoản nạp trước đó đã hoàn tiền. Bật lại bên dưới khi bạn muốn tiếp tục nạp tự động.
                    </p>
                    <div v-else-if="billing.autotopup.disabled_reason" class="banner"
                         :class="{'auth-warning':billing.autotopup.disabled_reason==='authentication_required'}"
                         style="margin:14px 0 0">
                      <template v-if="billing.autotopup.disabled_reason==='stripe_unconfirmed'">
                        Tự động nạp tiền tạm dừng vì không thể xác nhận thanh toán Stripe. Lệnh gọi có thể dừng khi hết số dư. Vui lòng kiểm tra lịch sử thanh toán hoặc liên hệ hỗ trợ.
                      </template>
                      <template v-else-if="billing.autotopup.disabled_reason==='authentication_required'">
                        Ngân hàng yêu cầu bạn xác thực thanh toán. Đã hủy lệnh tự động nạp này. Hãy nạp tiền thủ công để xác thực với ngân hàng; tự động nạp sẽ kích hoạt lại sau khi thành công.
                        <button class="btn primary" style="margin-left:10px" :disabled="billingBusy" @click="openTopup()">Nạp tiền thủ công</button>
                      </template>
                      <template v-else>
                        Tự động nạp tiền đã tắt ({{billing.autotopup.disabled_reason}}). Khi hết số dư, các lượt gọi công cụ sẽ dừng cho đến khi được nạp thêm.
                      </template>
                    </div>
                    <div v-else-if="billing.autotopup.enabled&&billing.autotopup.cap_reached" class="banner" style="margin:14px 0 0">
                      Lượt nạp tự động tiếp theo sẽ vượt hạn mức tháng {{money(billing.autotopup.monthly_cap_micro)}}, vì vậy hệ thống dừng nạp cho đến ngày 1 tháng sau (UTC).
                      <button class="btn primary" style="margin-left:10px" :disabled="billingBusy" @click="openTopup()">Nạp tiền thủ công</button>
                    </div>
                    <div style="margin-top:16px;border-top:1px solid var(--line);padding-top:14px">
                      <label style="display:flex;gap:10px;align-items:center;cursor:pointer">
                        <span class="tswitch"><input type="checkbox" :checked="billing.autotopup.enabled||autoOpen" :disabled="billingBusy" @change="autoToggled"/><span class="knob"></span></span>
                        <span class="lbl" style="margin:0">Tự động nạp tiền</span>
                        <span v-if="billing.card_on_file" class="sub saved-card-label">
                          <svg class="saved-card-check" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="m4 10 4 4 8-8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                          <span>Thẻ đã lưu với</span>
                          <img class="stripe-wordmark stripe-wordmark-slate" :src="stripeSlate" alt="Stripe">
                          <img class="stripe-wordmark stripe-wordmark-white" :src="stripeWhite" alt="Stripe">
                        </span>
                      </label>
                      <p class="sub" style="margin:8px 0 0">
                        <template v-if="billing.autotopup.enabled">Đang bật - tự động nạp {{money(billing.autotopup.amount_micro)}}<span v-if="tierBonus(billing.autotopup.amount_micro/1e6)" style="color:var(--green)"> + {{money(tierBonus(billing.autotopup.amount_micro/1e6))}} thưởng</span> mỗi khi số dư giảm xuống dưới {{money(billing.autotopup.threshold_micro)}}, tối đa {{billing.autotopup.per_hour}} lần mỗi giờ. Tháng này: {{money(billing.autotopup.month_spend_micro)}} trên hạn mức tháng {{money(billing.autotopup.monthly_cap_micro)}}.
                          <a href="#" @click.prevent="autoOpen=!autoOpen;autoConsent=false">{{autoOpen?'Hủy':'Chỉnh sửa'}}</a></template>
                        <template v-else>Duy trì hoạt động liên tục cho agent mà không cần theo dõi số dư. Chúng tôi chỉ trừ tiền thẻ đã lưu khi số dư giảm xuống dưới ngưỡng cài đặt.<template v-if="maxBonusPct"> Mức nạp lớn hơn nhận thêm tín dụng thưởng, lên tới +{{maxBonusPct}}% cho mỗi lần nạp.</template></template>
                      </p>
                      <p v-if="billing.autotopup.enabled&&!autoOpen&&nextBonusTier(billing.autotopup.amount_micro/1e6)" class="sub" style="margin:4px 0 0">
                        Nạp từ <b>${{nextBonusTier(billing.autotopup.amount_micro/1e6).usd}}</b> trở lên để nhận thêm <span style="color:var(--green)">+{{nextBonusTier(billing.autotopup.amount_micro/1e6).pct}}% thưởng</span> mỗi lần nạp.
                        <a href="#" @click.prevent="autoOpen=true;autoConsent=false">Đổi số tiền</a>
                      </p>
                      <!-- The same panel edits a running policy (Edit link above) and arms a new one:
                           either way the numbers change, so the mandate is re-agreed and re-stamped. -->
                      <div v-if="autoOpen" style="margin-top:12px;background:var(--panel2);border:1px solid var(--line);border-radius:var(--rb);padding:12px 14px;max-width:560px">
                        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
                          <span class="sub" style="margin:0">Nạp $</span>
                          <input class="msel" style="width:70px" type="number" min="5" v-model.number="autoAmount"/>
                          <span class="sub" style="margin:0">khi số dư giảm xuống dưới $</span>
                          <input class="msel" style="width:70px" type="number" min="5" v-model.number="autoThreshold"/>
                          <span class="sub" style="margin:0">, tối đa</span>
                          <input class="msel" style="width:56px" type="number" min="1" max="60" v-model.number="autoPerHour"/>
                          <span class="sub" style="margin:0">lần mỗi giờ</span>
                        </div>
                        <p class="sub" style="margin:8px 0 0">
                          <template v-if="tierBonus(autoAmount)">Mỗi lần nạp cộng <b>{{money(autoAmount*1e6+tierBonus(autoAmount))}}</b> ({{money(autoAmount*1e6)}} + <span style="color:var(--green)">{{money(tierBonus(autoAmount))}} thưởng</span>).</template>
                          <template v-if="nextBonusTier(autoAmount)"> Nạp <a href="#" @click.prevent="autoAmount=nextBonusTier(autoAmount).usd;autoConsent=false">${{nextBonusTier(autoAmount).usd}}</a> trở lên để nhận <span style="color:var(--green)">+{{nextBonusTier(autoAmount).pct}}% thưởng</span> mỗi lần nạp.</template>
                        </p>
                        <label style="display:flex;gap:8px;align-items:flex-start;margin-top:12px;cursor:pointer">
                          <input type="checkbox" v-model="autoConsent" style="margin-top:3px"/>
                          <!-- The mandate text. Not decoration: an off-session charge with no recorded
                               agreement to THESE numbers is an unauthorized charge under PSD2/SCA. -->
                          <span class="sub" style="margin:0">Tôi ủy quyền cho treg tự động trừ ${{autoAmount}} từ thẻ đã lưu mỗi khi số dư giảm xuống dưới ${{autoThreshold}}, tối đa {{autoPerHour}} lần mỗi giờ. Có thể hủy bất kỳ lúc nào.</span>
                        </label>
                        <div style="margin-top:12px">
                          <button class="btn primary" :disabled="!autoConsent||billingBusy" @click="setAuto(true)">{{billingBusy?'…':(billing.autotopup.enabled?'Lưu thay đổi':'Bật tự động nạp tiền')}}</button>
                        </div>
                      </div>
                    </div>

                    <div style="margin-top:16px;border-top:1px solid var(--line);padding-top:14px">
                      <div class="lbl">Lịch sử thanh toán</div>
                      <p class="sub" style="margin:8px 0 0">Các lượt nạp tiền sẽ cộng vào số dư công cụ. Gói đăng ký SSO được tính phí riêng.</p>
                      <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:12px" role="group" aria-label="Lọc giao dịch thanh toán">
                        <button v-for="filter in [{id:'all',label:'Tất cả'},{id:'manual',label:'Nạp thủ công'},{id:'auto',label:'Tự động nạp'},{id:'subscription',label:'Gói đăng ký'}]"
                                :key="filter.id" class="btn sm" :class="{primary:bhistFilter===filter.id}"
                                :aria-pressed="bhistFilter===filter.id" @click="setBillingHistoryFilter(filter.id)">{{filter.label}}</button>
                      </div>
                      <p v-if="bhist.loading" class="sub" style="margin:8px 0 0">Đang tải…</p>
                      <p v-else-if="bhist.error" class="sub" style="margin:8px 0 0">Không thể tải lịch sử thanh toán. <button class="btn sm" @click="loadBillingHistory()">Thử lại</button></p>
                      <p v-else-if="!bhist.items.length" class="sub" style="margin:8px 0 0">Chưa có giao dịch thanh toán nào trong mục này.</p>
                      <template v-else>
                        <!-- Top-up amounts come from our ledger; subscription invoices come from Stripe. -->
                        <div style="overflow-x:auto">
                        <table style="width:100%;min-width:440px;max-width:700px;margin-top:8px;border-collapse:collapse">
                          <thead><tr class="sub" style="text-align:left">
                            <th scope="col" style="padding:8px 10px 8px 0;font-weight:500">Ngày</th>
                            <th scope="col" style="padding:8px 10px 8px 0;font-weight:500">Số tiền</th>
                            <th scope="col" style="padding:8px 10px 8px 0;font-weight:500">Giao dịch</th>
                            <th scope="col" style="padding:8px 0;text-align:right;font-weight:500">Chứng từ</th>
                          </tr></thead>
                          <tbody>
                          <tr v-for="i in bhist.items" :key="i.id" style="border-top:1px solid var(--line)">
                            <td style="padding:8px 10px 8px 0;white-space:nowrap">{{bhistDate(i.created_at)}}</td>
                            <td style="padding:8px 10px 8px 0;font-family:var(--mono);white-space:nowrap">{{money(i.amount_micro)}}</td>
                            <td style="padding:8px 10px 8px 0;white-space:nowrap" class="sub">
                              {{i.kind==='subscription'?'Gói SSO':i.kind==='auto'?'Tự động nạp':'Nạp thủ công'}} ·
                              <span v-if="i.refunded_micro&&i.refunded_micro>=i.amount_micro">Đã hoàn tiền</span>
                              <span v-else :style="i.status==='paid'?'color:var(--green)':''">{{i.status==='paid'?'Đã thanh toán':i.status==='open'?'Chờ thanh toán':i.status||'Đang xử lý'}}</span>
                              <span v-if="i.kind==='subscription'&&i.number" class="muted"> · {{i.number}}</span>
                              <span v-if="i.bonus_micro&&!(i.refunded_micro>=i.amount_micro)" style="color:var(--green)"> +{{money(i.bonus_micro)}} thưởng</span>
                              <span v-if="i.refunded_micro&&i.refunded_micro<i.amount_micro"> · Đã hoàn {{money(i.refunded_micro)}}</span>
                            </td>
                            <td style="padding:8px 0;text-align:right;white-space:nowrap">
                              <a v-if="i.invoice_pdf||i.hosted_invoice_url" :href="i.invoice_pdf||i.hosted_invoice_url" target="_blank" rel="noopener">Hóa đơn</a>
                              <span v-if="(i.invoice_pdf||i.hosted_invoice_url)&&i.receipt_url" class="muted"> · </span>
                              <a v-if="i.receipt_url" :href="i.receipt_url" target="_blank" rel="noopener">Biên lai</a>
                              <span v-if="!(i.invoice_pdf||i.hosted_invoice_url||i.receipt_url)" class="muted">—</span>
                            </td>
                          </tr>
                          </tbody>
                        </table>
                        </div>
                      </template>
                      <p v-if="!bhist.ok && bhist.items.length" class="sub" style="margin:8px 0 0">Một số liên kết chứng từ nạp tiền tạm thời không khả dụng; số tiền nạp vẫn chính xác. Vui lòng thử lại hoặc dùng <b>Quản lý thanh toán</b>.</p>
                      <p v-if="!bhist.invoicesOk" class="sub" style="margin:8px 0 0">Hóa đơn gói đăng ký tạm thời không khả dụng. <button class="btn sm" @click="loadBillingHistory()">Thử lại</button></p>
                      <div v-if="!bhist.error && (bhistPage>0 || bhist.nextCursor)" style="display:flex;justify-content:flex-end;gap:8px;align-items:center;margin-top:14px">
                        <button class="btn sm" :disabled="bhistPage===0||bhist.loading" @click="previousBillingHistoryPage()">Trước</button>
                        <span class="sub" style="margin:0">Trang {{bhistPage+1}}</span>
                        <button class="btn sm" :disabled="!bhist.nextCursor||bhist.loading" @click="nextBillingHistoryPage()">Tiếp</button>
                      </div>
                    </div>
                  </template>

                </div>
              </div>
              <p v-else class="sub">Loading…</p>
            </template>

            <template v-if="canAdmin && orgTab==='projects'">
              <div class="lbl" style="margin-top:14px">Dự án</div>
              <p class="sub" style="margin:-2px 0 8px;font-size:12px">Dự án giúp gom nhóm công cụ trong đội ngũ, cho phép giới hạn quyền hạn của thành viên hoặc Agent theo từng dự án cụ thể. Công cụ không gán dự án sẽ hiển thị cho tất cả mọi người.</p>
              <div class="field" style="max-width:560px">
                <input v-model="projectName" placeholder="Tên dự án (vd: Apollo)" @keyup.enter="createProject"/>
                <button class="btn primary" @click="createProject" :disabled="projBusy">{{projBusy?'…':'Thêm dự án'}}</button>
              </div>
              <p v-if="!projects.length" class="muted" style="font-size:12px;margin-top:8px">Chưa có dự án nào — mọi công cụ đều áp dụng toàn đội ngũ.</p>
              <table v-else style="margin-top:8px">
                <tr><th>Dự án</th><th>Slug</th><th style="text-align:right">Công cụ</th><th></th></tr>
                <template v-for="p in projects" :key="p.id">
                <tr>
                  <td><b>{{p.name}}</b></td>
                  <td class="muted" style="font-family:var(--mono);font-size:12px">{{p.slug}}</td>
                  <td style="text-align:right">
                    <button class="btn sm" :class="{active:editProj===p.id}" @click="openProjTools(p)">{{p.tool_count}} công cụ ▾</button>
                  </td>
                  <td style="text-align:right">
                    <button class="btn sm" :class="{danger:confirmProj===p.id}" @click="deleteProject(p)" :title="'các '+p.tool_count+' công cụ sẽ trở về dùng chung toàn đội ngũ'">{{confirmProj===p.id?'Xác nhận xóa':'Xóa'}}</button>
                  </td>
                </tr>
                <tr v-if="editProj===p.id">
                  <td colspan="4" style="background:color-mix(in srgb,var(--accent) 5%,transparent)">
                    <div style="padding:6px 2px">
                      <div class="sub" style="margin-bottom:6px">Công cụ trong <b>{{p.name}}</b> — chọn để thêm, bỏ chọn để đưa về dùng chung toàn đội ngũ.</div>
                      <div v-if="!tools.length" class="muted" style="font-size:12px">Chưa có công cụ nào.</div>
                      <div style="display:flex;flex-wrap:wrap;gap:6px 16px">
                        <label v-for="t in tools" :key="t.id" class="tgl" style="min-width:190px">
                          <input type="checkbox" v-model="projToolDraft[t.id]"/><span>{{t.name}}</span>
                          <span v-if="t.project_id && t.project_id!==p.id" class="chip" style="margin-left:4px" :title="'hiện ở dự án '+projName(t.project_id)">{{projName(t.project_id)}}</span>
                        </label>
                      </div>
                      <div style="margin-top:10px;display:flex;gap:8px">
                        <button class="btn sm primary" @click="saveProjTools(p)" :disabled="projToolBusy">{{projToolBusy?'…':'Lưu'}}</button>
                        <button class="btn sm" @click="editProj=null">Hủy</button>
                      </div>
                    </div>
                  </td>
                </tr>
                </template>
              </table>

            </template>

            <!-- POLICY tab -->
            <template v-if="canAdmin && orgTab==='policy'">
              <div class="lbl" style="margin-top:14px">Chính sách chặn</div>
              <p class="sub" style="margin:-2px 0 8px;font-size:12px">Chặn cuộc gọi tới host, đường dẫn hoặc phương thức HTTP nhất định. Để trống nghĩa là áp dụng cho tất cả. Áp dụng cho proxy và lượt chạy CLI — với mọi người, bao gồm cả chủ sở hữu.</p>
              <div class="field" style="max-width:720px;flex-wrap:wrap">
                <input v-model="denyForm.host" placeholder="host (vd: api.stripe.com)" style="min-width:190px"/>
                <input v-model="denyForm.path_prefix" placeholder="đường dẫn (vd: /admin)" style="min-width:140px"/>
                <select v-model="denyForm.method" class="msel"><option value="">mọi phương thức</option><option>GET</option><option>POST</option><option>PUT</option><option>PATCH</option><option>DELETE</option></select>
                <select v-model="denyForm.user_id" class="msel" title="áp dụng cho ai">
                  <option :value="null">toàn đội ngũ</option>
                  <option v-for="m in rosterMembers.filter(x=>!x.is_observed)" :key="m.user_id" :value="m.user_id">{{m.is_agent?('agent: '+(m.name||m.email)):m.email}}</option>
                </select>
                <select v-if="projects.length" v-model="denyForm.project_id" class="msel" title="áp dụng cho công cụ dự án nào">
                  <option :value="null">mọi dự án</option>
                  <option v-for="p in projects" :key="p.id" :value="p.id">{{p.name}}</option>
                </select>
                <input v-model="denyForm.note" placeholder="lý do chặn (hiển thị khi từ chối)" style="min-width:170px"/>
                <button class="btn primary" @click="addDeny" :disabled="denyBusy">{{denyBusy?'…':'Chặn'}}</button>
              </div>
              <p v-if="!denyRules.length" class="muted" style="font-size:12px;margin-top:8px">Không có quy tắc nào — không có gì bị chặn.</p>
              <table v-else style="margin-top:8px">
                <tr><th>Phương thức</th><th>Host</th><th>Đường dẫn</th><th>Áp dụng cho</th><th v-if="projects.length">Dự án</th><th>Ghi chú</th><th></th></tr>
                <tr v-for="r in denyRules" :key="r.id">
                  <td><span class="chip">{{r.method||'mọi'}}</span></td>
                  <td style="font-family:var(--mono);font-size:12px">{{r.host||'mọi'}}</td>
                  <td style="font-family:var(--mono);font-size:12px">{{r.path_prefix||'mọi'}}</td>
                  <td>{{r.scope==='org'?'toàn đội ngũ':(denyWho(r.user_id))}}</td>
                  <td v-if="projects.length">{{r.project_id?projName(r.project_id):'mọi'}}</td>
                  <td class="muted" style="font-size:12px">{{r.note}}</td>
                  <td style="text-align:right"><button class="btn sm" :class="{danger:confirmDeny===r.id}" @click="removeDeny(r)">{{confirmDeny===r.id?'Xác nhận gỡ':'Gỡ bỏ'}}</button></td>
                </tr>
              </table>

              <!-- Tool-level argv blocks -->
              <template v-if="cliDeny.length">
                <div class="lbl" style="margin-top:22px">Quy tắc chặn CLI theo công cụ <span class="chip" style="margin-left:6px">chỉ đọc</span></div>
                <p class="sub" style="margin:-2px 0 8px;font-size:12px">treg chặn ở ba lớp: các quy tắc ở trên (HTTP host/path/method), các mẫu đối số CLI theo công cụ (từ treg.json của skill hoặc mặc định của catalog) và sandbox hệ điều hành.</p>
                <table>
                  <tr><th>Công cụ</th><th>Mẫu đối số bị chặn</th></tr>
                  <tr v-for="t in cliDeny" :key="t.tool">
                    <td><b>{{t.tool}}</b><span v-if="!t.enabled" class="chip" style="margin-left:6px" title="chạy local cho công cụ này chưa bật">tắt</span></td>
                    <td><span v-for="pat in t.patterns" :key="pat.pattern" class="chip" style="margin:2px 6px 2px 0;font-family:var(--mono);font-size:11px" :title="pat.source==='skill'?'từ treg.json của skill':'từ mặc định catalog'">{{pat.pattern}}<span class="muted" style="margin-left:4px">· {{pat.source}}</span></span></td>
                  </tr>
                </table>
              </template>
            </template>

            <!-- SHOWCASE: the team's apps on the public showcase (apply, edit, withdraw) -->
            <TeamShowcase v-if="canAdmin && orgTab==='showcase'" />

            <!-- TEAM SETTINGS: just the danger zone (new/join/switch team live in the sidebar
                 picker). Visible to every role — leaving a team is self-service, not admin. -->
            <template v-if="orgTab==='danger'">
            <!-- DAILY SPEND CAP. A team-level setting, so it lives here rather than under Billing.
                 It was invisible entirely before this, which meant a team first met it as an
                 unexplained 429; and it matters MOST when auto top-up is on, because a balance that
                 refills itself is no longer a ceiling and this becomes the only thing bounding a
                 runaway agent. `capCfg` is loaded by loadBilling(), which runs on every Team-page
                 load — NOT per tab — so it is populated by the time this renders.
                 NB the name: `orgSettings` is already a METHOD on this component (the ⚙ in the team
                 picker), and data and methods share one namespace. -->
            <div v-if="capCfg" style="margin-top:18px;border-top:1px solid var(--line);padding-top:14px">
                  <span class="lbl" style="margin:0">Hạn mức chi tiêu ngày</span>
                  <p class="sub" style="margin:4px 0 8px;font-size:12px">
                    Số tiền tối đa đội ngũ có thể chi tiêu mỗi ngày cho các lượt gọi trên khóa treg. Làm mới lúc 00:00 UTC. Mặc định không giới hạn.
                  </p>
                  <div class="field" style="max-width:560px">
                    <input v-model="capUsd" type="number" min="0" step="0.5" placeholder="không giới hạn" style="max-width:140px"/>
                    <button class="btn primary" :disabled="capBusy" @click="saveCap">{{capBusy?'…':'Lưu'}}</button>
                    <span class="sub" style="margin:0">
                      USD/ngày · hiện tại {{capCfg.daily_cap_micro ? money(capCfg.daily_cap_micro) : 'không giới hạn'}}<template v-if="!capCfg.daily_cap_set_by_team"> (mặc định)</template>
                    </span>
                  </div>
                  <p v-if="capErr" class="banner" style="margin:10px 0 0">{{capErr}}</p>
                  <p class="muted" style="font-size:12px;margin-top:8px">
                    Bất kỳ mức nào. Để trống (hoặc 0) nghĩa là không giới hạn — khi đó số dư là trần duy nhất.
                  </p>
                </div>

                <div v-if="capCfg" style="margin-top:22px;border-top:1px solid var(--line);padding-top:14px">
                  <span class="lbl" style="margin:0">Lưu trữ kết quả (Archive)</span>
                  <p class="sub" style="margin:4px 0 8px;font-size:12px">
                    treg lưu kết quả của các lượt gọi chính xác mà Agent gửi để phục vụ lần gọi lặp lại từ bộ nhớ đệm: miễn phí khi dùng khóa riêng của bạn, giảm giá khi dùng khóa của treg. Tắt tùy chọn này sẽ bỏ qua lưu trữ cả hai chiều.
                  </p>
                  <div class="field" style="max-width:560px;align-items:center">
                    <label class="tgl" :title="!canAdmin?'chỉ quản trị viên mới có quyền đổi':(capCfg.archive?'lưu trữ đang bật — bấm để tắt':'lưu trữ đang tắt — bấm để bật')">
                      <input type="checkbox" :checked="capCfg.archive" :disabled="archiveBusy || !canAdmin" @change="setArchive($event.target.checked)"/>
                      <span>{{capCfg.archive?'bật':'tắt'}}</span>
                    </label>
                    <span v-if="!canAdmin" class="sub" style="margin:0">chỉ admin có quyền đổi</span>
                  </div>
                  <p v-if="archiveErr" class="banner" style="margin:10px 0 0">{{archiveErr}}</p>
                </div>

                <div v-if="capCfg" style="margin-top:22px;border-top:1px solid var(--line);padding-top:14px">
                  <span class="lbl" style="margin:0">Hạn mức theo từng khách hàng (Tag Meta)</span>
                  <p class="sub" style="margin:4px 0 8px;font-size:12px">
                    Giới hạn hoặc chặn một khách hàng cụ thể dựa trên tag mà cuộc gọi gửi kèm (<code>X-Treg-Meta</code>).
                  </p>
                  <div class="field" style="max-width:680px;flex-wrap:wrap">
                    <select class="msel" v-model="budDim" style="max-width:160px">
                      <option v-for="k in budDims" :key="k" :value="k">{{k}}</option>
                    </select>
                    <input v-model="budVal" placeholder="cust_8123 — để trống = mặc định cho tất cả" style="max-width:230px"/>
                    <input v-model="budDaily" type="number" min="0" step="0.5" placeholder="USD/ngày" style="max-width:120px"/>
                    <button class="btn primary" :disabled="budBusy" @click="saveBudget()">{{budBusy?'…':'Thiết lập'}}</button>
                  </div>
                  <p v-if="budErr" class="banner" style="margin:10px 0 0">{{budErr}}</p>
                  <template v-for="dim in (capCfg.budget_dims||[])" :key="dim">
                    <table style="margin-top:10px">
                      <tr><th>{{dim}}</th><th style="text-align:right">Hạn mức ngày</th><th>Trạng thái</th><th></th></tr>
                      <tr>
                        <td><b>mọi {{dim}}</b> <span class="muted">(mặc định)</span></td>
                        <td style="text-align:right">{{defaultFor(dim)?fmtCap(defaultFor(dim)):'không giới hạn'}}</td>
                        <td><span class="muted">—</span></td>
                        <td style="text-align:right"><button v-if="defaultFor(dim)" class="btn sm" @click="removeBudget(defaultFor(dim))">Xóa</button></td>
                      </tr>
                      <tr v-for="b in overridesFor(dim)" :key="b.val">
                        <td style="padding-left:22px"><span class="chip">{{b.val}}</span></td>
                        <td style="text-align:right">{{fmtCap(b)}}</td>
                        <td><span class="badge" :class="b.status==='blocked'?'invalid':'ok'">{{b.status}}</span></td>
                        <td style="text-align:right;white-space:nowrap">
                          <button class="btn sm" @click="toggleBlock(b)">{{b.status==='blocked'?'Mở chặn':'Chặn'}}</button>
                          <button class="btn sm" @click="removeBudget(b)">Gỡ bỏ</button>
                        </td>
                      </tr>
                      <tr v-if="!overridesFor(dim).length"><td colspan="4" class="muted" style="font-size:12px">không có ngoại lệ — mọi {{dim}} đều tuân theo mặc định</td></tr>
                    </table>
                  </template>
                </div>


            <TeamAvatar v-if="canAdmin" />

            <div v-if="canAdmin && !isPersonal(activeOrg)" style="margin-top:18px;border-top:1px solid var(--line);padding-top:14px">
              <span class="lbl" style="margin:0">Tên đội ngũ và đường dẫn (slug)</span>
              <p class="sub" style="margin:4px 0 8px;font-size:12px">
                Slug là định danh của đội ngũ trong header <code>X-Treg-Org</code>, lệnh <code>treg org use</code> và MCP.
              </p>
              <div class="field" style="max-width:560px">
                <input v-model="renameName" placeholder="tên đội ngũ" maxlength="80" style="max-width:220px"/>
                <input v-model="renameSlug" placeholder="slug" maxlength="40" style="max-width:180px"/>
                <button class="btn primary" :disabled="renameBusy || !renameDirty" @click="renameOrg">{{renameBusy?'…':'Lưu'}}</button>
              </div>
              <p v-if="renameErr" class="sub" style="color:var(--red);margin:4px 0 0;font-size:12px">{{renameErr}}</p>
            </div>

            <template v-if="!isPersonal(activeOrg)">
            <div class="lbl" style="margin-top:14px;color:var(--red)">Vùng nguy hiểm</div>
            <div style="display:flex;gap:22px;flex-wrap:wrap;align-items:flex-start">
              <div>
                <button class="btn sm" :class="{danger:confirmLeave}" @click="leaveOrg">{{confirmLeave?'Xác nhận rời':'Rời đội ngũ'}}</button>
                <a v-if="confirmLeave" href="#" @click.prevent="confirmLeave=false" class="sub" style="margin-left:8px;font-size:12px">hủy</a>
              </div>
              <div v-if="isOwner" class="field" style="margin:0">
                <input v-model="confirmDel" :placeholder="'nhập '+activeSlugNow+' để xóa'" style="min-width:230px"/>
                <button class="btn sm danger" :disabled="confirmDel!==activeSlugNow" @click="deleteOrg">Xóa đội ngũ</button>
              </div>
            </div>
            </template>
            <p v-else class="sub" style="margin-top:14px;font-size:12px">Đội ngũ cá nhân không thể rời khỏi hoặc xóa. Tạo hoặc tham gia đội ngũ khác từ thanh chọn ở đầu trang.</p>
            </template>
          </div>

</template>

<style>
.saved-card-label { display:inline-flex; align-items:center; gap:5px; margin-left:auto; white-space:nowrap; }
.saved-card-check { width:15px; height:15px; color:var(--green); flex:none; }
.stripe-wordmark { width:38px; height:auto; display:block; }
.stripe-wordmark-slate { display:none; }
[data-theme="light"] .stripe-wordmark-slate { display:block; }
[data-theme="light"] .stripe-wordmark-white { display:none; }
</style>
