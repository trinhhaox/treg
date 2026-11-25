<script>
import { useDashboard } from '../state/context'
import { t } from '../state/i18n'
export default {
  setup(props, ctx) {
    const dash = useDashboard(props, ctx)
    return { ...dash, t }
  }
}
</script>

<template>

          <!-- Two programs, one page, forked at the header: the credit referral program every user
               gets, and the invite-only cash tier behind it. A fork rather than a card under the
               referral column, because a card there read as step four of the referral program. The
               cash tier is hand-approved on purpose — hand-approval IS the anti-gaming design
               (money.md §Referrals) — so it is a form, not a self-serve toggle, and it shows to
               everyone, team or not, so a partner without a team yet can still apply. -->
          <h1>{{refTab==='partner' ? t('referrals.partner_h1', 'Đối tác liên kết (Affiliate)') : t('referrals.friend_h1', 'Giới thiệu bạn bè')}}</h1>
          <p class="sub" v-if="refTab==='partner'">{{t('referrals.partner_sub', 'Revenue share, paid in cash. By invitation.')}}</p>
          <p class="sub" v-else :style="ref.loaded ? null : {visibility:'hidden'}">{{t('referrals.friend_sub_prefix', 'Friends get')}} {{money(ref.terms.referred_micro)}} {{t('referrals.friend_sub_mid', 'on their first $10 top-up. You get')}}
            {{money(ref.terms.referrer_micro)}},
            {{t('referrals.friend_sub_suffix', 'after a 7-day hold.')}}</p>
          <div class="tabs" style="max-width:720px">
            <button :class="{active:refTab==='friend'}" @click="refTab='friend'">{{t('referrals.tab_friend', 'Giới thiệu bạn bè')}}</button>
            <button :class="{active:refTab==='partner'}" @click="refTab='partner'">{{t('referrals.tab_partner', 'Đối tác liên kết')}}</button>
          </div>
          <div v-if="refTab==='partner'" style="max-width:720px">
            <div class="card">
              <div class="lbl">{{t('referrals.who_lbl', 'Dành cho ai')}}</div>
              <p class="sub" style="margin:6px 0 0">{{t('referrals.who_desc', 'Anyone with an audience: communities, newsletters, developer groups, agencies deploying AI for clients.')}}</p>
              <div class="lbl" style="margin-top:16px">{{t('referrals.what_lbl', 'Quyền lợi bạn nhận được')}}</div>
              <p class="sub" style="margin:6px 0 0">{{t('referrals.what_desc', 'A cut of top-ups from everyone you introduce, paid in cash monthly. Not credit, and no 20-referral cap.')}}</p>
              <div class="lbl" style="margin-top:16px">{{t('referrals.how_lbl', 'Cách thức tham gia')}}</div>
              <p class="sub" style="margin:6px 0 14px">{{t('referrals.how_desc', 'By invitation. Tell us about your audience and how you plan to introduce them to treg, and we\'ll be in touch.')}}</p>
              <a class="btn primary sm" href="https://forms.gle/5N3DyVPrNJkrGuxF6" target="_blank"
                 rel="noopener" @click="track('affiliate_apply_clicked')" style="text-decoration:none">{{t('referrals.apply_btn', 'Apply to be an affiliate partner')}}</a>
            </div>
            <p class="sub" style="margin:12px 0 0">{{t('referrals.friend_alt', 'Just want to refer a friend? The')}}
              <a href="#" @click.prevent="refTab='friend'">{{t('referrals.friend_alt_link', 'friend referral program')}}</a> {{t('referrals.friend_alt_tail', 'gives $5 credit per friend with no application.')}}</p>
          </div>

          <template v-if="refTab==='friend'">

          <p v-if="ref.loading" class="sub">{{t('common.loading', 'Đang tải…')}}</p>
          <div v-else style="max-width:720px">
            <div v-if="!ref.eligible" class="card" style="margin-top:14px">
              <div class="lbl">{{t('referrals.need_team_lbl', 'Tạo một đội ngũ để mở khóa liên kết giới thiệu')}}</div>
              <p class="sub" style="margin:6px 0 12px">{{t('referrals.need_team_desc', 'Phần thưởng giới thiệu được trả dưới dạng tín dụng vào đội ngũ mà bạn sở hữu, vì vậy bạn cần có một đội ngũ trước tiên.')}}</p>
              <button class="btn primary sm" @click="go('orgs')">{{t('referrals.go_orgs', 'Đi đến quản lý đội ngũ')}}</button>
            </div>

            <template v-else>
              <div class="card" style="margin-top:14px">
                <div class="lbl">{{t('referrals.link_lbl', 'Liên kết giới thiệu của bạn')}}</div>
                <div style="display:flex;gap:8px;margin-top:8px">
                  <input readonly :value="ref.link" @focus="$event.target.select()"
                         style="flex:1;min-width:0;font-family:var(--mono);font-size:12px">
                  <button class="btn sm" @click="copyRefLink" style="flex:none">{{refCopied ? t('common.copied', 'Đã chép') : t('common.copy', 'Sao chép')}}</button>
                </div>
                <p class="sub" style="margin:10px 0 0" v-if="ref.credit_org">
                  {{t('referrals.credit_to', 'Phần thưởng của bạn sẽ được cộng vào đội ngũ')}} <b>{{ref.credit_org.name}}</b>.</p>
              </div>

              <div class="statgrid" style="margin-top:14px;grid-template-columns:repeat(auto-fit,minmax(150px,1fr))">
                <div class="stat"><div class="n">{{ref.totals.signed_up}}</div><div class="l">{{t('referrals.stat_signed_up', 'đã đăng ký')}}</div></div>
                <div class="stat"><div class="n">{{ref.totals.topped_up}}</div><div class="l">{{t('referrals.stat_topped_up', 'đã nạp tiền')}}</div></div>
                <div class="stat"><div class="n">{{money(ref.totals.earned_micro)}}</div><div class="l">{{t('referrals.stat_earned', 'đã nhận thưởng')}}</div></div>
              </div>
              <p v-if="ref.totals.pending_micro" class="sub" style="margin:-8px 0 0">
                {{money(ref.totals.pending_micro)}} {{t('referrals.pending_notice', 'đang xử lý — phần thưởng sẽ mở khóa sau')}}
                {{ref.terms.hold_days}} {{t('referrals.days_since_topup', 'ngày kể từ khi bạn bè của bạn nạp tiền.')}}</p>

              <div v-if="ref.cap.limit != null && ref.cap.paid >= ref.cap.limit" class="card"
                   style="margin-top:14px;border-color:var(--accent)">
                <div class="lbl">{{t('referrals.cap_limit_title', 'hit the 20-referral limit')}}</div>
                <p class="sub" style="margin:6px 0 0">{{t('referrals.cap_limit_desc', 'That is the ceiling of the standard self-serve program. If you have a large audience, switch to the Affiliate partner tab above — we pay revenue share in cash.')}}</p>
              </div>

              <div class="grp" style="margin:20px 0 8px">Danh sách bạn bè đã giới thiệu</div>
              <p v-if="!ref.referrals.length" class="sub" style="margin:0">
                Chưa có ai. Hãy chia sẻ liên kết của bạn ở trên.</p>
              <table v-else>
                <tr><th>Người dùng</th><th>Ngày đăng ký</th><th>Trạng thái</th><th style="text-align:right">Tiền thưởng</th></tr>
                <tr v-for="(r,i) in ref.referrals" :key="i">
                  <td>{{r.email || '—'}}</td>
                  <td class="sub" style="white-space:nowrap">{{bhistDate(r.signed_up_at)}}</td>
                  <td>{{refStatus(r)}}</td>
                  <td style="text-align:right;font-family:var(--mono);white-space:nowrap">
                    <span v-if="r.reward_micro">{{money(r.reward_micro)}}</span>
                    <span v-else class="muted">—</span>
                  </td>
                </tr>
              </table>
            </template>
          </div>
          </template>

</template>
