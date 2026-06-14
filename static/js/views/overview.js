import store from "../accounts/store.js";
import { loadOverview } from "../accounts/accountService.js";

export default function overview(content) {

    function render(state) {

        const overview = state.overview;

        if (!overview) return;

        const { data, loading, error } = overview;

        // Loading
        if (loading) {
            content.innerHTML = `
                <div class="overview-loading">
                    <div class="spinner"></div>
                </div>
            `;
            return;
        }

        // Error
        if (error) {
            content.innerHTML = `
                <div class="overview-error">
                    <p>${error}</p>
                </div>
            `;
            return;
        }

        if (!data) return;

        const user = data.user;

        const avatar = "/static/images/picture.jpg";

        content.innerHTML = `
            <div class="overview-wrapper">

                <div class="overview-header">

                    <img 
                        src="${avatar}" 
                        class="overview-avatar"
                    />

                    <div class="overview-user-info">
                        <h2>
                            ${user.first_name} ${user.last_name}
                        </h2>

                        <p>
                            ${user.email}
                        </p>
                    </div>

                </div>


                <div class="overview-cards">

                    <div class="overview-card menu-link" data-section="personal">

                        <h3>Personal info</h3>

                        <p>
                            Manage your name, phone, and profile
                        </p>

                    </div>


                    <div class="overview-card menu-link" data-section="security">

                        <h3>Security</h3>

                        <p>
                            Change password and secure account
                        </p>

                    </div>


                    <div class="overview-card menu-link" data-section="settings">

                        <h3>Settings</h3>

                        <p>
                            Preferences and app settings
                        </p>

                    </div>

                </div>

            </div>
        `;
    }

    render(store.state);

    const unsubscribe = store.subscribe(render);

    loadOverview();

    return unsubscribe;
}
