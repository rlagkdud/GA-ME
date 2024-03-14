package ssafy.ggame.domain.user.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.oauth2.client.userinfo.DefaultOAuth2UserService;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserRequest;
import org.springframework.security.oauth2.core.OAuth2AuthenticationException;
import org.springframework.security.oauth2.core.user.DefaultOAuth2User;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Service;
import ssafy.ggame.domain.user.entity.User;
import ssafy.ggame.domain.user.repository.UserRepository;

import java.util.Collections;
import java.util.Map;

@Service
public class CustomOAuth2UserService extends DefaultOAuth2UserService {

    @Autowired
    private UserRepository userRepository;

    @Override
    public OAuth2User loadUser(OAuth2UserRequest userRequest) throws OAuth2AuthenticationException {
        OAuth2User oAuth2User = super.loadUser(userRequest);

        Map<String, Object> attributes = oAuth2User.getAttributes();
        String email = (String) attributes.get("email");
        String name = (String) attributes.get("name");
        String imageUrl = (String) attributes.get("picture");

        User user = userRepository.findByEmail(email)
                .map(entity -> updateExistingUser(entity, name, imageUrl))
                .orElseGet(() -> registerNewUser(email, name, imageUrl));

        return new DefaultOAuth2User(Collections.singleton(new SimpleGrantedAuthority("ROLE_USER")),
                attributes, "email");
    }

    private User registerNewUser(String email, String name, String imageUrl) {
        User user = new User();
        user.setEmail(email);
        user.setName(name);
        user.setImageUrl(imageUrl);
        return userRepository.save(user);
    }

    private User updateExistingUser(User existingUser, String name, String imageUrl) {
        existingUser.setName(name);
        existingUser.setImageUrl(imageUrl);
        return userRepository.save(existingUser);
    }
}